import os, sys, argparse, subprocess
import json
from dcicutils import ff_utils, s3_utils
import boto3

'''
Possible future upgrades:
- Build pubic docker image within post/patch script (would require Dockerfiles for each image)
- Replace try/except with query to database for the post/patch steps
'''

def main(ff_env='fourfront-cgapwolf', skip_software=False, skip_file_format=False,
         skip_workflow=False, skip_metaworkflow=False, skip_file_reference=False,
         skip_cwl=False, skip_ecr=False, cwl_bucket='', account='', region='',
         del_prev_version=False, ignore_key_conflict=False,
         ugrp_unrelated=False, action='store_true'):
    """post / patch contents from portal_objects to the portal"""

    if os.environ.get('GLOBAL_BUCKET_ENV', ''):  # new cgap account
        s3 = s3_utils.s3Utils(env=ff_env)
        keycgap = s3.get_access_keys('access_key_admin')
    else:
        keycgap = ff_utils.get_authentication_with_server(ff_env=ff_env)

    # Version
    with open("VERSION") as f:
        version = f.readlines()[0].strip()

    # Pipeline - REMOVE INPUT
    with open("PIPELINE") as f:
        pipeline = f.readlines()[0].strip()

    # Software
    if not skip_software:
        print("Processing software...")
        with open('portal_objects/software.json') as f:
            d = json.load(f)

        for dd in d:
            print("  processing uuid %s" % dd['uuid'])
            try:
                ff_utils.post_metadata(dd, 'Software', key=keycgap)
            except:
                ff_utils.patch_metadata(dd, dd['uuid'], key=keycgap)

    # File formats
    if not skip_file_format:
        print("Processing file format...")
        with open('portal_objects/file_format.json') as f:
            d = json.load(f)

        for dd in d:
            print("  processing uuid %s" % dd['uuid'])
            try:
                ff_utils.post_metadata(dd, 'FileFormat', key=keycgap)
            except Exception as e:
                if 'Keys conflict' in str(e):
                    if ignore_key_conflict:
                        pass
                    else:
                        raise(e)
                else:
                    ff_utils.patch_metadata(dd, dd['uuid'], key=keycgap)

    # Workflows
    if not skip_workflow: #going to add in PIPELINE replacement for ecr url.
        print("Processing workflow...")
        if cwl_bucket != '' and account != '' and region != '' and pipeline != '':
            wf_dir = "portal_objects/workflows"
            files = os.listdir(wf_dir)

            for fn in files:
                if fn.endswith('.json'):
                    print("  processing file %s" % fn)
                    with open(os.path.join(wf_dir, fn), 'r') as f:
                        d = json.load(f)

                    if del_prev_version:
                        # Clean previous version and aliases if present
                        if d.get('previous_version'):
                            del d['previous_version']
                        if d.get('aliases'):
                            d['aliases'] = [d['aliases'][0]]

                    # replace VERSION variable with correct version
                    d["aliases"][0] = d["aliases"][0].replace("VERSION",version)

                    for k in ["app_version", "docker_image_name", "name"]:
                        d[k] = d[k].replace("VERSION",version)

                    # replace CWLBUCKET and VERSION variables in cwl_directory_url_v1
                    d["cwl_directory_url_v1"] = d["cwl_directory_url_v1"].replace("CWLBUCKET", cwl_bucket).replace("PIPELINE", pipeline).replace("VERSION", version)

                    # replace ACCOUNT and VERSION variables for docker_image_name
                    account_region = account+".dkr.ecr."+region+".amazonaws.com"
                    d["docker_image_name"] = d["docker_image_name"].replace("ACCOUNT",account_region).replace("VERSION",version)

                    # Patch
                    try:
                        ff_utils.post_metadata(d, 'Workflow', key=keycgap)
                    except:
                        ff_utils.patch_metadata(d, d['uuid'], key=keycgap)
        else:
            # throw an error if the cwl bucket is not provided
            print("ERROR: when run without --skip-workflow, user must provide input for:\n    --cwl-bucket (user provided: "+cwl_bucket+")\n    --account (user provided: "+account+")\n    --region (user provided: "+region+")\n    --pipeline (user provied: "+pipeline+", choices are \'snv\' or \'sv\')")
            sys.exit(1)

    # File reference
    if not skip_file_reference:
        print("Processing file reference...")
        with open('portal_objects/file_reference.json') as f:
            d = json.load(f)

        for dd in d:
            print("  processing uuid %s" % dd['uuid'])
            try:
                ff_utils.post_metadata(dd, 'FileReference', key=keycgap)
            except:
                ff_utils.patch_metadata(dd, dd['uuid'], key=keycgap)

    # Metaworkflows
    if not skip_metaworkflow:
        print("Processing metaworkflow...")
        wf_dir = "portal_objects/metaworkflows"
        files = os.listdir(wf_dir)

        for fn in files:
            if fn.endswith('.json'):
                print("  processing file %s" % fn)
                with open(os.path.join(wf_dir, fn), 'r') as f:
                    d = json.load(f)
                    for k in ['title','version']:
                        d[k] = d[k].replace("VERSION", version)

                if del_prev_version:
                    # Clean previous version if present
                    if d.get('previous_version'):
                        del d['previous_version']

                if ugrp_unrelated:
                    uuid_ugrp_unrl = 'eac862c0-8c87-4838-83cb-9a77412bff6f'
                    for input in d['input']:
                        if input['argument_name'] == 'unrelated':
                            input['files'] = [{"file": uuid_ugrp_unrl}]

                try:
                    ff_utils.post_metadata(d, 'MetaWorkflow', key=keycgap)
                except:
                    ff_utils.patch_metadata(d, d['uuid'], key=keycgap)
    # CWLs
    if not skip_cwl:
        print("Processing cwl files...")
        if cwl_bucket != '' and account != '' and region != '' and pipeline != '':
            wf_dir = "cwl"
            s3 = boto3.resource('s3')
            #mk tmp dir for modified cwls
            os.mkdir(wf_dir+"/upload")
            account_region = account+".dkr.ecr."+region+".amazonaws.com"
            files = os.listdir(wf_dir)
            for fn in files:
                if fn.endswith('.cwl'):
                    # set original file path and path for s3
                    file_path = wf_dir+'/'+fn
                    s3_path_and_file = pipeline+'/'+version+'/'+fn

                    # separate workflows, which can be automatically uploaded to s3 without edits ...
                    if fn.startswith('workflow'):
                        print("  processing file %s" % fn)
                        s3.meta.client.upload_file(file_path, cwl_bucket, s3_path_and_file, ExtraArgs={'ACL':'public-read'})

                    # ... from CommandLineTool files which have the dockerPull that needs modification
                    else:
                        print("  processing file %s" % fn)
                        with open(file_path, 'r') as f:
                            with open(wf_dir+"/upload/"+fn, 'w') as w:
                                for line in f:
                                    if "dockerPull" in line:
                                        # modify line for output file by replacing generic variables
                                        line = line.replace("ACCOUNT",account_region).replace("VERSION",version)
                                    w.write(line)
                        # once modified, upload to s3
                        upload_path_and_file = wf_dir+"/upload/"+fn
                        s3.meta.client.upload_file(upload_path_and_file, cwl_bucket, s3_path_and_file, ExtraArgs={'ACL':'public-read'})

                        # delete file to allow tmp folder to be deleted at the end
                        os.remove(upload_path_and_file)

            # clean the directory from github repo
            os.rmdir(wf_dir+"/upload")
        else:
            # throw an error if the necessary input variables are not provided
            print("ERROR: when run without --skip-cwl, user must provide input for:\n    --cwl-bucket (user provided: "+cwl_bucket+")\n    --account (user provided: "+account+")\n    --region (user provided: "+region+")\n    --pipeline (user provied: "+pipeline+", choices are \'snv\' or \'sv\')")
            sys.exit(1)

    if not skip_ecr:
        print("Processing ECR images...")
        if account != '' and region != '' and pipeline != '':
            account_region = account+".dkr.ecr."+region+".amazonaws.com"
            # generic bash commands to be modified to correct version and account information
            snv_images = '''
            # login
            echo "For this to work, proper permissions are required within the EC2 environment"
            aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT

            # cgap on docker is snv on ECR
            docker pull cgap/cgap:VERSION
            docker tag cgap/cgap:VERSION ACCOUNT/snv:VERSION
            docker push ACCOUNT/snv:VERSION

            # md5 is same on docker and ECR
            docker pull cgap/md5:VERSION
            docker tag cgap/md5:VERSION ACCOUNT/md5:VERSION
            docker push ACCOUNT/md5:VERSION

            # fastqc is same on docker and ECR
            docker pull cgap/fastqc:VERSION
            docker tag cgap/fastqc:VERSION ACCOUNT/fastqc:VERSION
            docker push ACCOUNT/fastqc:VERSION
            '''

            sv_images = '''
            # login
            echo "For this to work, proper permissions are required within the EC2 environment"
            aws ecr get-login-password --region REGION | docker login --username AWS --password-stdin ACCOUNT

            # cgap-manta on docker is manta on ECR
            docker pull cgap/cgap-manta:VERSION
            docker tag cgap/cgap-manta:VERSION ACCOUNT/manta:VERSION
            docker push ACCOUNT/manta:VERSION

            # cnv is same on docker and ECR
            docker pull cgap/cnv:VERSION
            docker tag cgap/cnv:VERSION ACCOUNT/cnv:VERSION
            docker push ACCOUNT/cnv:VERSION
            '''

            if pipeline == 'snv':
                cmd = snv_images.replace("REGION", region).replace("ACCOUNT", account_region).replace("VERSION", version)
            # replace all variables
            elif pipeline == 'cnv':
                cmd = sv_images.replace("REGION", region).replace("ACCOUNT", account_region).replace("VERSION", version)

            # push create and push images
            subprocess.check_call(cmd, shell=True)

            print("ECR images created!")
        else:
            # throw an error if the cwl bucket is not provided
            print("ERROR: when run without --skip-ecr, user must provide input for:\n    --account (user provided: "+account+")\n    --region (user provided: "+region+")\n    --pipeline (user provied: "+pipeline+", choices are \'snv\' or \'sv\')")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ff-env', default='fourfront-cgapwolf')
    parser.add_argument('--skip-software', action='store_true')
    parser.add_argument('--skip-file-format', action='store_true')
    parser.add_argument('--skip-workflow', action='store_true')
    parser.add_argument('--skip-metaworkflow', action='store_true')
    parser.add_argument('--skip-file-reference', action='store_true')
    parser.add_argument('--skip-cwl', action='store_true')
    parser.add_argument('--skip-ecr', action='store_true')
    parser.add_argument('--cwl-bucket', default='')
    parser.add_argument('--account', default='')
    parser.add_argument('--region', default='')
    parser.add_argument('--del-prev-version', action='store_true')
    parser.add_argument('--ignore-key-conflict', action='store_true')
    parser.add_argument('--ugrp-unrelated', action='store_true')

    args = parser.parse_args()
    main(ff_env=args.ff_env, skip_software=args.skip_software,
         skip_file_format=args.skip_file_format, skip_workflow=args.skip_workflow,
         skip_metaworkflow=args.skip_metaworkflow, skip_file_reference=args.skip_file_reference,
         skip_cwl=args.skip_cwl, skip_ecr=args.skip_ecr, cwl_bucket=args.cwl_bucket, account=args.account,
         region=args.region, del_prev_version=args.del_prev_version,
         ignore_key_conflict=args.ignore_key_conflict, ugrp_unrelated=args.ugrp_unrelated)
