#!/usr/bin/env bash

set -u  # treat unset variable references as errors

# set -e is omitted so that the script continues even if one rclone call fails

REMOTE="remote:emory-rodgerslab-backup-hot-20221205"

# Absolute path so cron writes the log somewhere predictable regardless of
# what directory cron happens to run the script from
LOG_FILE="/volume1/homes/chris/rclone_backup.log"

# Flags passed to every rclone copy call:
#   --skip-links          : ignore symlinks entirely (avoids a warning)
#   --exclude @eaDir/**   : skip Synology's @eaDir folders
#   --modify-window 1ms   : tolerance for mtime comparison between source and
#                           destination. Many files were originally uploaded
#                           from an sshfs mount and mtimes differ by <1ms.
#   --fast-list           : fetch the full remote object listing in one API
#                           call rather than paginating. Uses more memory but
#                           is faster and reduces API request costs.
#   --log-file            : append rclone output to this file
#   --log-level INFO      : log informational messages (transfers, skips)
#   --stats-one-line      : print transfer statistics on a single line
RCLONE_OPTS=(
    --dry-run
    --skip-links
    --exclude="@eaDir/**"
    --modify-window=1ms
    --fast-list
    --log-file="$LOG_FILE"
    --log-level=INFO
    --stats-one-line
)

# Directories to back up.
# Each entry is the full absolute path on this server.
# The remote destination name is derived from the basename of each path
# (see loop below), so /volume1/homes/abigail backs up to $REMOTE/abigail.
BACKUP=(
    /volume1/homes/abigail
    /volume1/homes/abr
    /volume1/homes/behavior
    /volume1/homes/cedric
    /volume1/homes/chris
    /volume1/homes/christina
    /volume1/homes/cici
    /volume1/homes/lucas
    /volume1/homes/nanoz
    /volume1/homes/octopus
    /volume1/homes/rowan
    /volume1/homes/shared
    /volume1/homes/sukrith
    /volume1/homes/surgery
    /volume1/homes/whitematter
    /volume1/homes/whitematter_D
    /volume2/lucasX
    /volume2/shrimpX
    /volume2/sukrithX
)

# Directories intentionally excluded from backup -- no warning will be emitted.
# Move to BACKUP above as needed.
SKIP_SILENT=(
    /volume1/homes/@eaDir
    /volume1/homes/admin
    /volume1/homes/pineapple
    /volume1/homes/carrissa
    /volume1/homes/cem
    /volume1/homes/devinenilab
    /volume1/homes/drew
    /volume1/homes/dyerlab
    /volume1/homes/eliana
    /volume1/homes/farscape
    /volume1/homes/halcyon
    /volume1/homes/jessica
    /volume1/homes/joseph
    /volume1/homes/kai
    /volume1/homes/megan
    /volume1/homes/osama
    /volume1/homes/shrimp
    /volume1/homes/valentina
    /volume2/@eaDir
    /volume2/@sharesnap
    /volume2/@tmp
    /volume2/expansion
    /volume3/@eaDir
    /volume3/@tmp
    /volume3/small
)

# -- Scan for unclassified directories -----------------------------------------
#
# Safety net: warns about any directory not explicitly listed in BACKUP or
# SKIP_SILENT. Catches new directories (e.g. a new lab member's home folder)
# that haven't been deliberately classified yet.

SCAN_ROOTS=( /volume1/homes /volume2 /volume3 )

for ROOT in "${SCAN_ROOTS[@]}"; do
    for DIR in "$ROOT"/*/; do

        # Strip the trailing slash that the glob adds
        DIR="${DIR%/}"

        # Warn and skip if the glob matched something that isn't a real
        # directory (e.g. a broken symlink)
        if [[ ! -d "$DIR" ]]; then
            echo "WARNING: not a directory, skipping: $DIR"
            continue
        fi

        # This is for checking whether the dir is in either list
        in_backup=0
        in_skip=0

        # Check if it's in BACKUP
        for b in "${BACKUP[@]}"; do
            [[ "$b" == "$DIR" ]] && in_backup=1 && break
        done
        
        # Check if it's in SKIP_SILENT
        for s in "${SKIP_SILENT[@]}"; do
            [[ "$s" == "$DIR" ]] && in_skip=1 && break
        done

        # A directory in both arrays is a configuration mistake -- warn and
        # skip it rather than silently backing it up or silently ignoring it
        if (( in_backup && in_skip )); then
            echo "WARNING: $DIR appears in both BACKUP and SKIP_SILENT," \
                 "remove it from one of the arrays"
        elif (( !in_backup && !in_skip )); then
            echo "WARNING: unclassified directory, not backed up: $DIR"
        fi
    done
done

echo "The following directories will be backed up:"
printf '%s\n' "${BACKUP[@]}"

# -- Run backups ----------------------------------------------------------------

# Sentinel lines make it easy to grep the cron log for run boundaries and timing
echo "AUTORUN_START__"
echo "AUTORUN_START_TIME : $(date +%F_%H-%M-%S)"

# realpath "$0" resolves the script's absolute path, so the log shows exactly
# which file was run even if invoked via a symlink or relative path
echo "AUTORUN_SCRIPT : $(realpath "$0")"

FAILED=()

for SRC in "${BACKUP[@]}"; do
    # basename extracts the final path component: /volume1/homes/abigail -> abigail
    # This becomes the subdirectory name at the remote destination
    NAME=$(basename "$SRC")
    echo "--- syncing: $SRC"

    # Echo the exact rclone call before running it, so the log shows what was
    # executed if you need to reproduce or debug a specific transfer
    echo "    rclone copy ${RCLONE_OPTS[@]} $SRC $REMOTE/$NAME"

    # Block comment this section to skip any actual rclone calls
    if ! rclone copy "${RCLONE_OPTS[@]}" "$SRC" "$REMOTE/$NAME"; then
        echo "ERROR: rclone failed for $SRC"
        FAILED+=("$SRC")
    fi

	exit 1
done

if (( ${#FAILED[@]} > 0 )); then
    echo "AUTORUN_FAILED_DIRS: ${FAILED[*]}"
fi

echo "AUTORUN_STOP_TIME $(date +%F_%H-%M-%S)"
echo "AUTORUN_STOP__"
