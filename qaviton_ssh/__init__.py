import io
import select
from os.path import exists
from paramiko import client, RSAKey
from paramiko.channel import ChannelFile, ChannelStderrFile, Channel


# && -> is a cross-platform solution that will execute the next command, if the previous had no errors.
# you may change it...
# ; -> in linux will execute regardless of error codes
# & -> in windows will execute regardless of error codes
MULTI_COMMAND_OPERATOR = ' && '


class Response:
    def __init__(self, stdin: ChannelFile, stdout: ChannelFile, stderr: ChannelStderrFile, timeout):
        # get the shared channel for stdout/stderr/stdin
        channel: Channel = stdout.channel
        channel.settimeout(timeout)

        # we do not need stdin.
        stdin.close()
        # indicate that we're not going to write to that channel anymore
        channel.shutdown_write()

        # read stdout/stderr in order to prevent read block hangs
        stdout_chunks = [stdout.channel.recv(len(stdout.channel.in_buffer))]
        stderr_chunks = []
        # chunked read to prevent stalls
        while not channel.closed or channel.recv_ready() or channel.recv_stderr_ready():
            # stop if channel was closed prematurely, and there is no data in the buffers.
            got_chunk = False
            readq, _, _ = select.select([stdout.channel], [], [], timeout)
            for c in readq:
                if c.recv_ready():
                    stdout_chunks.append(stdout.channel.recv(len(c.in_buffer)))
                    got_chunk = True
                if c.recv_stderr_ready():
                    # make sure to read stderr to prevent stall
                    stderr_chunks.append(stderr.channel.recv_stderr(len(c.in_stderr_buffer)))
                    got_chunk = True
            '''
            1) make sure that there are at least 2 cycles with no data in the input buffers in order to not exit too early (i.e. cat on a >200k file).
            2) if no data arrived in the last loop, check if we already received the exit code
            3) check if input buffers are empty
            4) exit the loop
            '''
            if not got_chunk \
            and stdout.channel.exit_status_ready() \
            and not stderr.channel.recv_stderr_ready() \
            and not stdout.channel.recv_ready():
                # indicate that we're not going to read from this channel anymore
                stdout.channel.shutdown_read()
                # close the channel
                stdout.channel.close()
                break  # exit as remote side is finished and our buffers are empty

        # close all the pseudo files
        stdout.close()
        stderr.close()
        
        self.data: bytes = b''.join(stdout_chunks)
        self.error: bytes = b''.join(stderr_chunks)


class SSH:
    """ Create your SSH Instance """
    # @classmethod
    # def set_pkey(cls, key_file):
    #     cls.default_pkey = RSAKey.from_private_key_file(key_file)

    def __init__(self, hostname: str, username: str, private_key: str, port: int = 22, timeout: float = 60.0):
        if exists(private_key):
            with open(private_key) as f:
                private_key = f.read()
        pkey = RSAKey.from_private_key(io.StringIO(private_key))

        # if key_file is None:
        #     pkey = NodeSSH.default_pkey
        # else:
        #     pkey = RSAKey.from_private_key_file(key_file)

        self.timeout = timeout
        self.client = client.SSHClient()
        self.client.set_missing_host_key_policy(client.AutoAddPolicy())
        self.client.connect(hostname, username=username, port=port, timeout=timeout, pkey=pkey)
        # self.sftp = self.client.open_sftp()

    def __enter__(self): return self
    def __exit__(self): ...
    def __del__(self):
        try: self.close()
        except: ...

    # TODO: needs to be tested
    # def create_session(self):
    #     session = self.client.get_transport().open_session(timeout=self.timeout)
    #     session.settimeout(self.timeout)
    #     return SessionSSH(session)

    def close(self): self.client.close()

    def send(self, command, timeout=None):
        """ execute remote command """
        return Response(*self.client.exec_command(command, timeout=timeout))

    def send_many(self, commands: list, timeout=None, command_sep=MULTI_COMMAND_OPERATOR):
        """ execute remote commands """
        return Response(*self.client.exec_command(command_sep.join(commands), timeout=timeout))


# TODO: needs to be tested
# class SessionSSH:
#     def __enter__(self): return self
#     def __exit__(self, exc_type, exc_val, exc_tb): pass
#
#     def __del__(self):
#         try: self.close()
#         except: pass
#
#     def __init__(self, session: Channel):
#         self.session = session
#
#     def close(self): self.session.close()
#
#     def send(self, command):
#         """ execute remote command"""
#         self.session.exec_command(command)
#         stdin = self.session.makefile("wb", -1)
#         stdout = self.session.makefile("r", -1)
#         stderr = self.session.makefile_stderr("r", -1)
#         return Response(stdin, stdout, stderr)


# TODO: make async SSH
