import argparse
import glob
import os
import shutil
import sys

E_NO_SRC_TRY_GLOBBING = 1
E_NO_SRC_EVEN_AFTER_GLOBBING = 2
E_NO_DST_TRY_MAKEDIR = 3
E_NO_DST_TRY_MAKEDIRS = 4
E_DST_EXISTS_TRY_OVERWRITE = 5
E_NOT_IMPLEMENTED_YET = 101

def create_parser():
	p = argparse.ArgumentParser(description="This is a tool to be used e.g. from makefiles which need to execute shell commands in a portable way. Its only requirement being, obviously, Python.", epilog="Type `appveyor.py command -h` for details on a subcommand.")
	p.add_argument("--dry-run", help="do NOT write to disk, just simulate", action="store_true")
	p.add_argument("--verbose", help="describe what you are doing; useful with `--dry-run`", action="store_true")

	s = p.add_subparsers(title="commands", dest="cmd")

	c = s.add_parser("cp", help="copy a file")
	c.set_defaults(func=on_cp_cmd)
	c.add_argument("src", help="source file to be copied")
	c.add_argument("dst", help="target dir to be copied to")
	c.add_argument("--no-glob", help="don't expand wildcards in `src` path", action="store_true")
	c.add_argument("--no-makedir", help="expect `dst` path to exist", action="store_true")
	c.add_argument("--no-makedirs", help="don't make intermediate dirs in `dst` path", action="store_true")
	c.add_argument("--force-overwrite", help="overwrite existing destination file", action="store_true")

	c = s.add_parser("md", help="make a dir")
	c.set_defaults(func=on_md_cmd)

	c = s.add_parser("rm", help="drop a file or dir")
	c.set_defaults(func=on_rm_cmd)

	return p

def on_cp_cmd(p, aa):
	if aa.no_glob:
		src = aa.src
		if not os.path.isfile(src):
			fail(E_NO_SRC_TRY_GLOBBING, 'The `src` path ("%s") does not point at a file. Try leaving `--no-glob` out.' % src)
	else:
		src = glob.glob(aa.src)
		if not src:
			fail(E_NO_SRC_EVEN_AFTER_GLOBBING, 'The `src` path ("%s") doesn\'t point at anything (even after globbing).' % aa.src)
		else:
			src = src[0]

	src = os.path.abspath(src)
	dst = os.path.abspath(aa.dst)

	inform(aa, 'Source file will be "%s".' % src)

	if not os.path.exists(dst):
		inform(aa, 'Path "%s" does not point at a directory.' % dst)

		if aa.no_makedir:
			inform(aa, "Flag `--no-makedir` was specified: nothing can be done.")
			fail(E_NO_DST_TRY_MAKEDIR, 'The value in `dst` ("%s") is not a dir. If you want to automatically build the path, leave `--no-makedir` out.' % dst)

		if aa.no_makedirs:
			inform(aa, 'Flag `--no-makdirs` was specified: trying to satisfy requirements by building a single directory.')
			try: os.mkdir(dst)
			except WindowsError as e:
				if 3 == e.winerror:
					fail(E_NO_DST_TRY_MAKEDIRS, 'The path in `dst` ("%s") does not point at a directory. Since you\'ve left `--no-makedir` out, normally it would be generated, The path, however, is deeper than a single level. Hence, to automatically build the entire tree, including all sub-directories, you will need to leave `--no-makdirs` out as well.' % dst)
				else: raise
		else:
			inform(aa, 'Building directory tree: "%s".' % dst)
			os.makedirs(dst)

	dst = os.path.join(dst, os.path.split(src)[1])
	inform(aa, 'Destination file will be at "%s".' % dst)

	if os.path.exists(dst):
		if aa.force_overwrite:
			inform(aa, 'A file is already present at target path "%s", but flag `--force-overwrite` was set: target file will be overwritten.' % dst)
		else:
			fail(E_DST_EXISTS_TRY_OVERWRITE, 'Flag `--force-overwrite` has not been set but a file is already present at target path "%s": nothing to be done.' % dst)

	if aa.dry_run:
		inform(aa, 'Would be copying "%s" to "%s" (if `--dry-run` wasn\'t specified).' % (src, dst))
	else:
		if aa.force_overwrite:
			inform(aa, 'Copying "%s" to "%s" (overwriting the previous version).' % (src, dst))
		else:
			inform(aa, 'Copying "%s" to "%s".' % (src, dst))

		shutil.copy(src, dst)

def on_md_cmd(p, aa):
	fail(E_NOT_IMPLEMENTED_YET, 'Command `md` was not implemented yet.')

def on_rm_cmd(p, aa):
	fail(E_NOT_IMPLEMENTED_YET, 'Command `rm` was not implemented yet.')

def inform(aa, text):
	if aa.verbose:
		print "[verbose] %s" % text

def fail(*aa):
	if len(aa) == 1:
		fail_1(*aa)
	elif len(aa) == 2:
		fail_2(*aa)
	else:
		print "[ERROR] %s" % str(aa)

def fail_1(text):
	print "[error] %s" % str(text)
	exit(-1)

def fail_2(code, text):
	print "[error %d] %s" % (code, str(text))
	exit(code)

def main(args=sys.argv[1:]):
	p = create_parser()
	aa = p.parse_args(args)
	print aa
	aa.func(p, aa)

	# if "cp" == aa.cmd:
	# 	on_cp_cmd(p, aa)

if "__main__" == __name__:
	main()
