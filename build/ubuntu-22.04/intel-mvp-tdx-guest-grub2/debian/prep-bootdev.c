#include <stdio.h>
#include <stdlib.h>
#include <parted/parted.h>

int
main(int argc, char *argv[])
{
	PedDevice *dev;

	ped_exception_fetch_all();
	ped_device_probe_all();
	for (dev = ped_device_get_next(NULL); dev;
	     dev = ped_device_get_next(dev)) {
		PedDisk *disk;
		PedPartition *part;

		disk = ped_disk_new(dev);
		if (!disk)
			continue;

		for (part = ped_disk_next_partition(disk, NULL); part;
		     part = ped_disk_next_partition(disk, part)) {
			if (ped_partition_is_active(part) &&
			    ped_partition_get_flag(part, PED_PARTITION_PREP)) {
				char *path;

				path = ped_partition_get_path(part);
				if (path) {
					printf("%s\n", path);
					free(path);
					return 0;
				}
				free(path);
			}
		}
	}

	return 0;
}
