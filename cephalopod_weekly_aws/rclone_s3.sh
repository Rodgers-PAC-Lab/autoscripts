echo AUTORUN_START__
echo AUTORUN_START_TIME : `date +%F_%H-%M-%S`
echo AUTORUN_SCRIPT : $(realpath "$0")
rclone copy --log-file=rclone.log ~/mnt/cuttlefish/abigail remote:emory-rodgerslab-backup-hot-20221205/abigail
rclone copy --log-file=rclone.log ~/mnt/cuttlefish/behavior remote:emory-rodgerslab-backup-hot-20221205/behavior
rclone copy --log-file=rclone.log ~/mnt/cuttlefish/carrissa remote:emory-rodgerslab-backup-hot-20221205/carrissa
rclone copy --log-file=rclone.log ~/mnt/cuttlefish/cedric remote:emory-rodgerslab-backup-hot-20221205/cedric
rclone copy --log-file=rclone.log ~/mnt/cuttlefish/chris remote:emory-rodgerslab-backup-hot-20221205/chris
rclone copy --log-file=rclone.log ~/mnt/cuttlefish/devinenilab remote:emory-rodgerslab-backup-hot-20221205/devinenilab
rclone copy --log-file=rclone.log ~/mnt/cuttlefish/osama remote:emory-rodgerslab-backup-hot-20221205/osama
rclone copy --log-file=rclone.log ~/mnt/cuttlefish/rowan remote:emory-rodgerslab-backup-hot-20221205/rowan
rclone copy --log-file=rclone.log ~/mnt/cuttlefish/whitematter remote:emory-rodgerslab-backup-hot-20221205/whitematter
echo AUTORUN_STOP_TIME `date +%F_%H-%M-%S`
echo AUTORUN_STOP__
