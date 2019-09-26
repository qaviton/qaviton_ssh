import io
from paramiko import client, RSAKey
from paramiko.channel import ChannelFile, ChannelStderrFile, Channel


CHANNEL_RECV_BUFFER = 1024  # TODO: maybe we should calculate the system's best buffer size with some weak estimation?

# && -> is a cross-platform solution that will execute the next command
# if the previous had no errors. you may change it...
# ; -> in linux will execute regardless of error codes
# & -> in windows will execute regardless of error codes
MULTI_COMMAND_OPERATOR = ' && '


class Response:
    def __init__(self, stdin: ChannelFile, stdout: ChannelFile, stderr: ChannelStderrFile):
        channel: Channel = stdout.channel
        data = err = b''
        while not channel.exit_status_ready():

            # collect stdout data when available
            if channel.recv_ready():
                # Retrieve the first CHANNEL_RECV_BUFFER bytes
                data += channel.recv(CHANNEL_RECV_BUFFER)
                while channel.recv_ready():
                    # Retrieve the next CHANNEL_RECV_BUFFER bytes
                    data += channel.recv(CHANNEL_RECV_BUFFER)

            # collect stderr data when available
            if channel.recv_stderr_ready():
                # Retrieve the first CHANNEL_RECV_BUFFER bytes
                err += channel.recv_stderr(CHANNEL_RECV_BUFFER)
                while channel.recv_stderr_ready():
                    # Retrieve the next CHANNEL_RECV_BUFFER bytes
                    err += channel.recv_stderr(CHANNEL_RECV_BUFFER)

        # collect stdout data when available
        if channel.recv_ready():
            # Retrieve the first CHANNEL_RECV_BUFFER bytes
            data += channel.recv(CHANNEL_RECV_BUFFER)
            while channel.recv_ready():
                # Retrieve the next CHANNEL_RECV_BUFFER bytes
                data += channel.recv(CHANNEL_RECV_BUFFER)

        # collect stderr data when available
        if channel.recv_stderr_ready():
            # Retrieve the first CHANNEL_RECV_BUFFER bytes
            err += channel.recv_stderr(CHANNEL_RECV_BUFFER)
            while channel.recv_stderr_ready():
                # Retrieve the next CHANNEL_RECV_BUFFER bytes
                err += channel.recv_stderr(CHANNEL_RECV_BUFFER)

        self.data: bytes = data
        self.error: bytes = err


class SSH:
    """ Create your SSH Instance """
    # @classmethod
    # def set_pkey(cls, key_file):
    #     cls.default_pkey = RSAKey.from_private_key_file(key_file)

    def __init__(self, hostname: str, username: str, private_key: str, port: int = 22, timeout: float = 60.0):
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
    def __exit__(self, exc_type, exc_val, exc_tb): pass
    def __del__(self):
        try: self.close()
        except: pass

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
