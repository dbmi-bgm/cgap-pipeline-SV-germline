import os
import json
from dcicutils import ff_utils, s3_utils
import argparse


def main(ff_env='fourfront-cgapwolf', skip_software=False, skip_file_format=False,
         skip_workflow=False, skip_metaworkflow=False, skip_file_reference=False,
         del_prev_version=False, ignore_key_conflict=False, ugrp_unrelated=False):
    """post / patch contents from portal_objects to the portal"""

    if os.environ.get('GLOBAL_BUCKET_ENV', ''):  # new cgap account
        s3 = s3_utils.s3Utils(env=ff_env)
        keycgap = s3.get_access_keys('access_key_admin')
    else:
        keycgap = ff_utils.get_authentication_with_server(ff_env=ff_env)

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
    if not skip_workflow:
        print("Processing workflow...")
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

                # Patch
                try:
                    ff_utils.post_metadata(d, 'Workflow', key=keycgap)
                except:
                    ff_utils.patch_metadata(d, d['uuid'], key=keycgap)

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

                if ugrp_unrelated:
                    uuid_ugrp_unrl = 'fcd6a543-fe49-4d32-b569-1d63db7176d3'
                    for input in d['input']:
                        if input['argument_name'] == 'unrelated':
                            input['files'] = [{"file": uuid_ugrp_unrl}]

                try:
                    ff_utils.post_metadata(d, 'MetaWorkflow', key=keycgap)
                except:
                    ff_utils.patch_metadata(d, d['uuid'], key=keycgap)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--ff-env', default='fourfront-cgapwolf')
    parser.add_argument('--skip-software', action='store_true')
    parser.add_argument('--skip-file-format', action='store_true')
    parser.add_argument('--skip-workflow', action='store_true')
    parser.add_argument('--skip-metaworkflow', action='store_true')
    parser.add_argument('--skip-file-reference', action='store_true')
    parser.add_argument('--del-prev-version', action='store_true')
    parser.add_argument('--ignore-key-conflict', action='store_true')
    parser.add_argument('--ugrp-unrelated', action='store_true')
    args = parser.parse_args()
    main(ff_env=args.ff_env, skip_software=args.skip_software,
         skip_file_format=args.skip_file_format, skip_workflow=args.skip_workflow,
         skip_metaworkflow=args.skip_metaworkflow, skip_file_reference=args.skip_file_reference,
         del_prev_version=args.del_prev_version, ignore_key_conflict=args.ignore_key_conflict,
         ugrp_unrelated=args.ugrp_unrelated)
