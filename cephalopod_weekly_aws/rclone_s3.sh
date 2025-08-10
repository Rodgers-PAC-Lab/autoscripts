# This one runs every 4 days
# Comment out whitematter because that one runs nightly

echo AUTORUN_START__
echo AUTORUN_START_TIME : `date +%F_%H-%M-%S`
echo AUTORUN_SCRIPT : $(realpath "$0")
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/abigail remote:emory-rodgerslab-backup-hot-20221205/abigail
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/abr remote:emory-rodgerslab-backup-hot-20221205/abr
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/behavior remote:emory-rodgerslab-backup-hot-20221205/behavior
#rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/carrissa remote:emory-rodgerslab-backup-hot-20221205/carrissa
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/cedric remote:emory-rodgerslab-backup-hot-20221205/cedric
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/chris remote:emory-rodgerslab-backup-hot-20221205/chris
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/devinenilab remote:emory-rodgerslab-backup-hot-20221205/devinenilab
#rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/eliana remote:emory-rodgerslab-backup-hot-20221205/eliana
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/joseph remote:emory-rodgerslab-backup-hot-20221205/joseph
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/kai remote:emory-rodgerslab-backup-hot-20221205/kai
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/lucas remote:emory-rodgerslab-backup-hot-20221205/lucas
#rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/megan remote:emory-rodgerslab-backup-hot-20221205/megan
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/nanoz remote:emory-rodgerslab-backup-hot-20221205/nanoz
#rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/osama remote:emory-rodgerslab-backup-hot-20221205/osama
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/rowan remote:emory-rodgerslab-backup-hot-20221205/rowan
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/shared remote:emory-rodgerslab-backup-hot-20221205/shared
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/sukrith remote:emory-rodgerslab-backup-hot-20221205/sukrith
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/surgery remote:emory-rodgerslab-backup-hot-20221205/surgery
#rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/valentina remote:emory-rodgerslab-backup-hot-20221205/valentina
#rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/whitematter remote:emory-rodgerslab-backup-hot-20221205/whitematter
rclone copy --fast-list --log-file=rclone.log --log-level INFO ~/mnt/cuttlefish/whitematter_D remote:emory-rodgerslab-backup-hot-20221205/whitematter_D
echo AUTORUN_STOP_TIME `date +%F_%H-%M-%S`
echo AUTORUN_STOP__
