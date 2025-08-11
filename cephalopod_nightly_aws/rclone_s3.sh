# rclone only the neural data, which is at highest risk of being overwritten
echo AUTORUN_START__
echo AUTORUN_START_TIME : `date +%F_%H-%M-%S`
echo AUTORUN_SCRIPT : $(realpath "$0")
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/whitematter remote:emory-rodgerslab-backup-hot-20221205/whitematter
echo AUTORUN_STOP_TIME `date +%F_%H-%M-%S`
echo AUTORUN_STOP__
