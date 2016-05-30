from subprocess import *


class transmission_remote_controller():
    def __init__(self, password):
        # if transmission-daemon not running, start it.
        self.password = password
        procout = self.run_process(["service", "transmission-daemon", "status"])
        if 'Active: active' in procout:
            print('transmission-daemon is already active\n')
        elif 'Active: inactive' in procout:
            print('inactive, starting daemon')
            self.start_daemon()
        else:
            print('error getting daemon status')

    def sudo_run_process(self, commands, withsudo, password):
        # echo 'password' | sudo -S command
        commands = ['sudo', '-S'] + commands
        if withsudo:
            with Popen(['echo', password], stdout=PIPE) as echo, Popen(commands, stdin=echo.stdout,
                                                                       stdout=PIPE) as proc:
                out = (proc.stdout.read())
            return (out.decode('utf-8'))

    def run_process(self, commands):
        with Popen(commands, stdout=PIPE) as proc:
            out = (proc.stdout.read())
        return (out.decode('utf-8'))

    def start_daemon(self):
        procout = self.sudo_run_process(["service", "transmission-daemon", "start"], True, self.password)

    def stop_daemon(self):
        procout = self.sudo_run_process(["service", "transmission-daemon", "stop"], True, self.password)

    def parse_list_output(self, lines):
        split_lines = [line.split() for line in lines]
        return [
            {
                'ID': line[0],
                'DONE_PERCENTAGE': line[1],
                'DONE_TOTAL': line[2],
                'DONE_UNIT': line[3],
                'ETA': line[4],
                'UP': line[5],
                'DOWN': line[6],
                'RATIO': line[7],
                'STATUS': line[8],
                'NAME': ''.join(line[9:])
            }

            for line in split_lines
            ]

    def get_torrent_list(self):
        procout = self.run_process(['transmission-remote', '-n', 'transmission:transmission', '-l'])
        lines = procout.split('\n')
        lines.pop()  # remove last line, it's blank
        named_colums = lines.pop(0).split()
        summary = lines.pop().split()
        parsed = self.parse_list_output(lines)
        return parsed

    def remove_torrent(self, id):
        procout = self.run_process(['transmission-remote', '-n', 'transmission:transmission', '-t', str(id), '-r'])

    def add_torrent(self, link, download_limit, directory):
        procout = self.run_process(
            ['transmission-remote', '-n', 'transmission:transmission', '-a', link, '-d', str(download_limit), '-w',
             directory])
