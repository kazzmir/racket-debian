# Date as YYYYMMDD
def todays_date():
    import datetime
    return datetime.date.today().strftime('%Y%m%d')

def iso_date():
    import datetime
    # hour/minute/second will be 0 because today() only has info about y/m/d
    return datetime.date.today().strftime('%a, %d %b %Y %H:%M:%S -0600')
    # If we really cared about the format we can use date -R
    # import subprocess
    #return subprocess.check_output(['date'], ['-R'])

def setup_changelog(version, date, distro):
    data = """racket (%(version)s-%(date)s~%(distro)s) %(distro)s; urgency=low

  * New packaging

 -- Jon Rafkind <jon@rafkind.com>  %(iso-date)s
""" % {'version' : version,
       'distro' : distro,
       'date': date,
       'iso-date': iso_date()}

    out = open('work/plt/debian/changelog', 'w')
    out.write(data)
    out.close()

def run_debuild():
    import os
    import subprocess
    os.chdir('work/plt')
    subprocess.call(['debuild', '-S'])
    os.chdir('../..')

def upload(date, version, distro, ppa):
    import os
    file = "work/racket_%(version)s-%(date)s~%(distro)s_source.changes" % {'version' : version, 'date' : date, 'distro' : distro}
    if not os.path.exists(file):
        raise Exception("Could not find `%s'. Something went terribly wrong!" % file)
    import subprocess
    subprocess.call(['dput', 'ppa:plt/%s' % ppa, file])

def find_plt_version():
    import re
    version = re.compile('#define MZSCHEME_VERSION "(.*)"')
    file = open('work/plt/src/racket/src/schvers.h')
    for line in file.readlines():
        out = version.match(line)
        if out:
            file.close()
            return out.group(1)
    file.close()
    raise Exception('Could not find version!')

def slurp(path):
    file = open(path)
    out = file.read()
    file.close()
    return out

def create(distro, ppa):
    date = todays_date()
    version = find_plt_version()
    setup_changelog(version, date, distro)
    run_debuild()
    upload(date, version, distro, ppa)

def create_nightly(distro):
    create(distro, 'racket-nightly')

def rebuild_work_directory():
    import shutil, os
    shutil.rmtree('work', ignore_errors = True)
    os.mkdir('work')

def setup_plt_directory(branch):
    def pull_latest_git(branch):
        import os
        import subprocess
        subprocess.call(['git', 'clone', '-b', 'stable', 'https://github.com/plt/racket/', 'plt'])
        #os.chdir('plt')
        #subprocess.call(['git', 'pull'])
        #subprocess.call(['git', 'checkout', branch])
        #subprocess.call(['git', 'fetch'])
        #subprocess.call(['git', 'merge', 'origin/%s' % branch])
        #os.chdir('..')

    def copy_git_tree():
        import shutil, os
        print "Copying plt tree"
        shutil.rmtree('work', ignore_errors = True)
        os.mkdir('work')
        shutil.copytree('plt', 'work/plt')
        shutil.rmtree('work/plt/.git', ignore_errors = True)
        print "Copying debian directory"
        shutil.copytree('debian', 'work/plt/debian')

    def patch_configure():
        import os, subprocess
        data = slurp('configure.patch')
        os.chdir('work/plt')
        process = subprocess.Popen(['patch', '-p1'], stdin = subprocess.PIPE)
        process.communicate(data)
        process.wait()
        os.chdir('../..')

    pull_latest_git(branch)
    copy_git_tree()
    patch_configure()

obsolete = ['oneiric', 'maverick', 'karmic']
distros = ['lucid', 'raring', 'quantal', 'precise', 'saucy']
