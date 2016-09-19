import yaml
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler
from threading import Thread
from Queue import Queue, Empty
from subprocess import call
from time import sleep
from sys import argv, exit
from functools import partial
import getopt


def service_dependent_paths(yaml):
    for service_name, definition in yaml.iteritems():
        build = definition.get('build')
        paths = []
        if build:
            if isinstance(build, basestring):
                paths.append(build)
            else:
                context = build['context']
                paths.append(context)
                dockerfile = build.get('dockerfile')
                if dockerfile and not dockerfile.startswith(context):
                    paths.append(dockerfile)
        yield service_name, paths


class BuildEventHandler(PatternMatchingEventHandler):
    def __init__(self, rebuild_service, service_name, **kwargs):
        self.rebuild_service = rebuild_service
        self.service_name = service_name
        PatternMatchingEventHandler.__init__(self, **kwargs)

    def on_any_event(self, event):
        self.rebuild_service(self.service_name)


def rebuild_service(call_compose, service_name):
    call_compose('stop', '-t', '0', service_name)
    call_compose('rm', '-f', service_name)
    call_compose('build', service_name)
    call_compose('up', '-d', service_name)


def execute_rebuild_debounced(rebuild_service, queue):
    def get(*args):
        item = queue.get(*args)
        if item is None:
            raise StopIteration
        return item

    while True:
        try:
            pending_calls = [get(True)]
            while True:
                try:
                    pending_calls.append(get(True, 0.1))
                except Empty:
                    break
            already_called = set()
            for call in pending_calls:
                if call not in already_called:
                    rebuild_service(call)
                    already_called.add(call)
        except StopIteration:
            break


def usage():
    print """Usage: docker-compose-watch [opts]
    -f, --file FILE            Alternate docker compose file
    -i, --ignore PATTERN       Specify patterns to ignore
    -o, --only PATTERN         Specify patterns to watch
    -h, --help                 Show this help listing
    """

def main():
    try:
        opts, args = getopt.getopt(argv[1:], 'hf:i:o:', ('help', 'file=', 'ignore=', 'only='))
    except getopt.GetoptError as err:
        print str(err)
        usage()
        exit(2)

    if args:
        print "Unknown positional argument(s)" % ', '.join(args)
        usage()
        exit(2)

    docker_compose_file = 'docker-compose.yml'
    ignore_patterns = []
    patterns = []
    verbose = False
    for opt, value in opts:
        if opt in ('-h', '--help'):
            usage()
            exit()
        elif opt in ('-f', '--file'):
            docker_compose_file = value
        elif opt in ('-i', '--ignore'):
            ignore_patterns.append(value)
        elif opt in ('-o', '--only'):
            patterns.append(value)
        else:
            assert False, 'unhandled option'
    ignore_patterns = ignore_patterns or None
    patterns = patterns or None

    try:
        docker_compose_yaml = yaml.load(file(docker_compose_file))
    except:
        print "Failed to load docker compose YAML file '%s'" % docker_compose_file
        exit(2)

    def call_compose(*args):
        call(('docker-compose', '-f', docker_compose_file) + args)


    rebuild_queue = Queue()
    observer = Observer()
    for service_name, paths in service_dependent_paths(docker_compose_yaml):
        if paths:
            handler = BuildEventHandler(rebuild_queue.put, service_name, ignore_patterns=ignore_patterns,
                                                                         patterns=patterns)
            for path in paths:
                observer.schedule(handler, path, recursive=True)

    try:
        observer.start()
        call_compose('build')
        call_compose('up', '-d')
        Thread(target=call_compose, args=('logs', '--follow')).start()
        Thread(target=execute_rebuild_debounced, args=(partial(rebuild_service, call_compose),
                                                       rebuild_queue)).start()
        while True:
            sleep(1)
    except KeyboardInterrupt:
        pass

    rebuild_queue.put(None)
    call_compose('stop')
    observer.stop()
    observer.join()


if __name__ == '__main__':
    main()
