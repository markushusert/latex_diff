#!/usr/bin/python
import argparse
import os
import subprocess
default_diffname="diff"
parser = argparse.ArgumentParser(description='Program designed to highlight differences between two latex-projects')
parser.add_argument('orig',
                    help='path to main .tex-file of original latex-project')
parser.add_argument('changed',
                    help='path to main .tex-file of changed latex-projects')
parser.add_argument("-o",'--output',
                    help=f'path to project containing the differences, if not given os.path.dirname(changed)/{default_diffname} will be used')
args = parser.parse_args()

def run_bash_cmd(cmd,dir="."):
    #
    if dir=="":
        dir="."
    #print(f"cmd:{cmd},dir:{dir}")
    subprocess.run(cmd,cwd=dir,capture_output=False,shell=True,executable="/bin/bash")
def generate_list_of_used_files(main_tex_file):
    used_files=[]
    used_filestructure=recreate_used_filestructure(main_tex_file)

    for dir,_,files in os.walk(used_filestructure):
        for file in files:
            used_files.append(os.path.join(dir,file))
            
    return used_files,used_filestructure
def recreate_used_filestructure(main_tex_file):
    """
    creates filestructure of latex-document using mkjobtexmf, and returns path to create .mjt directory
    """
    main_tex_dir=os.path.dirname(main_tex_file)
    main_tex_without_ext=os.path.basename(main_tex_file).split(".")[0]
    run_bash_cmd(f"mkjobtexmf --jobname {main_tex_without_ext}",main_tex_dir)
    return os.path.join(main_tex_dir,main_tex_without_ext+".mjt")
def main():
    changed_files,changed_basedir=generate_list_of_used_files(args.changed)
    orig_files,orig_basedir=generate_list_of_used_files(args.orig)

    if args.output is not None:
        target_dir=args.output
    else:
        target_dir=os.path.join(os.path.dirname(args.changed),default_diffname)
    os.makedirs(target_dir,exist_ok=True)

    rel_paths_orig={os.path.relpath(file,orig_basedir) for file in orig_files}
    rel_paths_changed={os.path.relpath(file,changed_basedir) for file in changed_files}
    all_paths_of_project=rel_paths_orig.union(rel_paths_changed)


    for rel_path in all_paths_of_project:
        orig_file=os.path.join(orig_basedir,rel_path)
        changed_file=os.path.join(changed_basedir,rel_path)
        output_file=os.path.join(target_dir,rel_path)
        outputdir=os.path.dirname(output_file)
        os.makedirs(outputdir,exist_ok=True)

        try:
            os.remove(output_file)
        except OSError:
            pass

        #texfiles processed via latexdiff
        if (rel_path.endswith(".tex")):
            for file in [orig_file,changed_file]:
                if not os.path.exists(file):
                    open(file,"w").close()#create empty file if not existent
        
            run_bash_cmd(f"latexdiff {orig_file} {changed_file} >{output_file}")
        #other files (images are just linked)
        else:
            if os.path.exists(changed_file):
                os.symlink(os.path.relpath(changed_file,outputdir),output_file)
            elif os.path.exists(orig_file):
                os.symlink(os.path.relpath(orig_file,outputdir),output_file)
            


if __name__=="__main__":
    main()
