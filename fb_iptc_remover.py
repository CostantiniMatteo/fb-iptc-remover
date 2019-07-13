#!/usr/bin/env python3

import os, argparse, imghdr, binascii
from iptcinfo3 import IPTCInfo

def process_file(curr_dir, file, random_replace=False, verbose=False):
            if verbose:
                print(" -- File:", file, end=' (')

            filepath = os.path.join(curr_dir, file)
            img_type = imghdr.what(filepath)

            if img_type is not None:
                if verbose:
                    print(img_type, end='). ')

                info = IPTCInfo(filepath, force=True)

                special_instructions = info['special instructions']
                if special_instructions is None:
                    if verbose:
                        print("FBMD not found")
                    return

                fbmd_index = special_instructions.find(b'FBMD')
                if fbmd_index < 0:
                    if verbose:
                        print("FBMD not found")
                    return

                length_hex = special_instructions[fbmd_index + 6: fbmd_index + 6 + 4]
                length = int(length_hex, 16)

                info['special instructions'] = update_instructions(
                    special_instructions, fbmd_index, length, random=random_replace
                )

                if verbose:
                    print(
                        special_instructions[fbmd_index: fbmd_index + 6 + 4 + (length + 1) * 8]
                    )

                info.save()
                os.remove(filepath + "~")
            else:
                if verbose:
                    print("Skipping).")

def process_directory(root, recursive=False, random_replace=False, verbose=False):
    for curr_dir, subdirs, files in os.walk(root):
        if verbose:
            print("Directory:", curr_dir)

        for file in files:
            process_file(curr_dir, file, random_replace, verbose)

        if not recursive:
            break

def update_instructions(special_instructions, idx, length, random=False):
    if not random:
        return special_instructions[:idx] + \
            special_instructions[idx + 6 + 4 + (length + 1)*8:]

    return special_instructions[idx:idx + 6 + 4] + \
        binascii.b2a_hex(os.urandom((length + 1)*4))

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--recursive', dest='recursive',
        action='store_true', default=False)
    parser.add_argument('--random-replace', dest='random_replace',
        action='store_true', default=False)
    parser.add_argument('-v', '--verbose', dest='verbose',
        action='store_true', default=False)
    parser.add_argument('rootdir', nargs=1)
    args = parser.parse_args()

    process_directory(
        args.rootdir[0],
        recursive=args.recursive,
        random_replace=args.random_replace,
        verbose=args.verbose
    )
