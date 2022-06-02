/* 915resolution - Utility to change vbemodes on the intel
 * integrated video chipset */

/*
 * Based on Nathan Coulson's http://nathancoulson.com/proj/eee/grub-1.96-915resolution-0.5.2-3.patch
 * Oct 10, 2008, Released as 915
 * Oct 10, 2008, Updated to include support for 945GM thanks to Scot Doyle
 */

/* Copied from 915 resolution created by steve tomjenovic
 * 915 resolution was in the public domain.
 * 
 * All I have done, was make the above program run within 
 * the grub2 environment.  
 *
 * Some of the checks are still commented, as I did not find
 * easy replacement for memmem.
 *
 * Slightly edited by Nathan Coulson (conathan@gmail.com)
 */

/*
 *  GRUB  --  GRand Unified Bootloader
 *  Copyright (C) 2003,2007  Free Software Foundation, Inc.
 *  Copyright (C) 2003  NIIBE Yutaka <gniibe@m17n.org>
 *
 *  GRUB is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 *
 *  GRUB is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 *  GNU General Public License for more details.
 *
 *  You should have received a copy of the GNU General Public License
 *  along with GRUB.  If not, see <http://www.gnu.org/licenses/>.
 */


/* 915 resolution by steve tomljenovic
 *
 * This was tested only on Sony VGN-FS550.  Use at your own risk
 *
 * This code is based on the techniques used in :
 *
 *   - 855patch.  Many thanks to Christian Zietz (czietz gmx net)
 *     for demonstrating how to shadow the VBIOS into system RAM
 *     and then modify it.
 *
 *   - 1280patch by Andrew Tipton (andrewtipton null li).
 *
 *   - 855resolution by Alain Poirier
 *
 * This source code is into the public domain.
 */

#include <grub/types.h>
#include <grub/misc.h>
#include <grub/mm.h>
#include <grub/err.h>
#include <grub/dl.h>
#include <grub/normal.h>
#include <grub/i386/io.h>

GRUB_MOD_LICENSE ("GPLv3+");

#define printf					grub_printf
#define malloc					grub_malloc
#define free					grub_free
#define strcmp					grub_strcmp
#define fprintf(stream, ...)			grub_printf(__VA_ARGS__)
#define strtol(x,y,z)				grub_strtoul(x,y,z)
#define atoi(x)					grub_strtoul(x,NULL,10)
#define assert(x)				
#define memset					grub_memset
#define outl		grub_outl
#define outb		grub_outb
#define inl		grub_inl
#define inb		grub_inb

#define NEW(a) ((a *)(malloc(sizeof(a))))
#define FREE(a) (free(a))

#define VBIOS_START         0xc0000
#define VBIOS_SIZE          0x10000

#define VBIOS_FILE    "/dev/mem"

#define FALSE 0
#define TRUE 1

#define MODE_TABLE_OFFSET_845G 617

#define RES915_VERSION "0.5.3"

#define ATI_SIGNATURE1 "ATI MOBILITY RADEON"
#define ATI_SIGNATURE2 "ATI Technologies Inc"
#define NVIDIA_SIGNATURE "NVIDIA Corp"
#define INTEL_SIGNATURE "Intel Corp"

#define DEBUG 0

typedef unsigned char * address;
typedef unsigned char byte;
typedef unsigned short word;
typedef unsigned char boolean;
typedef unsigned int cardinal;

typedef enum {
    CT_UNKWN, CT_830, CT_845G, CT_855GM, CT_865G, CT_915G, CT_915GM, CT_945G, CT_945GM, CT_945GME,
    CT_946GZ, CT_G965, CT_Q965, CT_965GM, CT_G33, CT_Q33, CT_Q35, CT_500GMA,
    CT_GM45,  CT_GMA3150, CT_HD3000
} chipset_type;

const char *const chipset_type_names[] = {
    "UNKNOWN", "830",  "845G", "855GM", "865G", "915G", "915GM", "945G", "945GM", "945GME",
    "946GZ",   "G965", "Q965", "965GM", "G33", "Q33", "Q35", "500GMA",
    "GM45",    "GMA3150", "HD3000"
};

typedef enum {
    BT_UNKWN, BT_1, BT_2, BT_3
} bios_type;

const char *const bios_type_names[] = {"UNKNOWN", "TYPE 1", "TYPE 2", "TYPE 3"};

int freqs[] = { 60, 75, 85 };

typedef struct {
    byte mode;
    byte bits_per_pixel;
    word resolution;
    byte unknown;
} __attribute__((packed)) vbios_mode;

typedef struct {
    byte unknow1[2];
    byte x1;
    byte x_total;
    byte x2;
    byte y1;
    byte y_total;
    byte y2;
} __attribute__((packed)) vbios_resolution_type1;

typedef struct {
    unsigned long clock;

    word x1;
    word htotal;
    word x2;
    word hblank;
    word hsyncstart;
    word hsyncend;

    word y1;
    word vtotal;
    word y2;
    word vblank;
    word vsyncstart;
    word vsyncend;
} __attribute__((packed)) vbios_modeline_type2;

typedef struct {
    byte xchars;
    byte ychars;
    byte unknown[4];

    vbios_modeline_type2 modelines[];
} __attribute__((packed)) vbios_resolution_type2;

typedef struct {
    unsigned long clock;

    word x1;
    word htotal;
    word x2;
    word hblank;
    word hsyncstart;
    word hsyncend;

    word y1;
    word vtotal;
    word y2;
    word vblank;
    word vsyncstart;
    word vsyncend;

    word timing_h;
    word timing_v;

    byte unknown[6];
} __attribute__((packed)) vbios_modeline_type3;

typedef struct {
    unsigned char unknown[6];

    vbios_modeline_type3 modelines[];
} __attribute__((packed)) vbios_resolution_type3;


typedef struct {
    cardinal chipset_id;
    chipset_type chipset;
    bios_type bios;
    
    int bios_fd;
    address bios_ptr;

    vbios_mode * mode_table;
    cardinal mode_table_size;

    byte b1, b2;

    boolean unlocked;
} vbios_map;


static cardinal get_chipset_id(void) {
    outl(0x80000000, 0xcf8);
    return inl(0xcfc);
}

static chipset_type get_chipset(cardinal id) {
    chipset_type type;
    
    switch (id) {
    case 0x35758086:
        type = CT_830;
        break;

    case 0x25608086:
        type = CT_845G;
        break;
        
    case 0x35808086:
        type = CT_855GM;
        break;
        
    case 0x25708086:
        type = CT_865G;
        break;

    case 0x25808086:
	type = CT_915G;
	break;

    case 0x25908086:
        type = CT_915GM;
        break;

    case 0x27708086:
        type = CT_945G;
        break;

    case 0x27a08086:
        type = CT_945GM;
        break;

    case 0x27ac8086:
        type = CT_945GME;
        break;

    case 0x29708086:
        type = CT_946GZ;
        break;

    case 0x29a08086:
	type = CT_G965;
	break;

    case 0x29908086:
        type = CT_Q965;
        break;

    case 0x2a008086:
        type = CT_965GM;
        break;

    case 0x29c08086:
        type = CT_G33;
        break;

    case 0x29b08086:
        type = CT_Q35;
        break;

    case 0x29d08086:
        type = CT_Q33;
        break;

    case 0x81008086:
      type = CT_500GMA;
      break;

    case 0xa0008086:
        type = CT_GMA3150;
        break;

    case 0xa0108086:
        type = CT_GMA3150;
        break;

    case 0x01048086:
        type = CT_HD3000;
        break;

    case 0x2a408086:
        type = CT_GM45;
        break;

    case 0x2a018086:
        type = CT_965GM;
        break;

    case 0x2a028086:
        type = CT_965GM;
        break;

    default:
        type = CT_UNKWN;
        break;
    }

    return type;
}


static vbios_resolution_type1 * map_type1_resolution(vbios_map * map, word res) {
    vbios_resolution_type1 * ptr = ((vbios_resolution_type1*)(map->bios_ptr + res)); 
    return ptr;
}

static vbios_resolution_type2 * map_type2_resolution(vbios_map * map, word res) {
    vbios_resolution_type2 * ptr = ((vbios_resolution_type2*)(map->bios_ptr + res)); 
    return ptr;
}

static vbios_resolution_type3 * map_type3_resolution(vbios_map * map, word res) {
    vbios_resolution_type3 * ptr = ((vbios_resolution_type3*)(map->bios_ptr + res)); 
    return ptr;
}


static boolean detect_bios_type(vbios_map * map, int entry_size) {
    unsigned i;
    short int r1, r2;
    
    r1 = r2 = 32000;

    for (i=0; i < map->mode_table_size; i++) {
        if (map->mode_table[i].resolution <= r1) {
            r1 = map->mode_table[i].resolution;
    	}
        else {
            if (map->mode_table[i].resolution <= r2) {
            	r2 = map->mode_table[i].resolution;
            }
    	}

        /*printf("r1 = %d  r2 = %d\n", r1, r2);*/
    }

    return (r2-r1-6) % entry_size == 0;
}


static void close_vbios(vbios_map * map);


static vbios_map * open_vbios(chipset_type forced_chipset) {
    vbios_map * map = NEW(vbios_map);
    memset (map, 0, sizeof(vbios_map));

    /*
     * Determine chipset
     */

    if (forced_chipset == CT_UNKWN) {
        map->chipset_id = get_chipset_id();

        map->chipset = get_chipset(map->chipset_id);
    }
    else if (forced_chipset != CT_UNKWN) {
        map->chipset = forced_chipset;
    }
    else {
        map->chipset = CT_915GM;
    }
    
    /*
     *  Map the video bios to memory
     */

    map->bios_ptr = (unsigned char *) VBIOS_START;

#if 0
    /*
     * check if we have ATI Radeon
     */
    
    if (memmem(map->bios_ptr, VBIOS_SIZE, ATI_SIGNATURE1, strlen(ATI_SIGNATURE1)) ||
        memmem(map->bios_ptr, VBIOS_SIZE, ATI_SIGNATURE2, strlen(ATI_SIGNATURE2)) ) {
        fprintf(stderr, "ATI chipset detected.  915resolution only works with Intel 800/900 series graphic chipsets.\n");
        close(map->bios_fd);
        exit(2);
    }

    /*
     * check if we have NVIDIA
     */
    
    if (memmem(map->bios_ptr, VBIOS_SIZE, NVIDIA_SIGNATURE, strlen(NVIDIA_SIGNATURE))) {
        fprintf(stderr, "NVIDIA chipset detected.  915resolution only works with Intel 800/900 series graphic chipsets.\n");
        close(map->bios_fd);
        exit(2);
    }

    /*
     * check if we have Intel
     */
    
    if (map->chipset == CT_UNKWN && memmem(map->bios_ptr, VBIOS_SIZE, INTEL_SIGNATURE, strlen(INTEL_SIGNATURE))) {
        fprintf(stderr, "Intel chipset detected.  However, 915resolution was unable to determine the chipset type.\n");

        fprintf(stderr, "Chipset Id: %x\n", map->chipset_id);

        fprintf(stderr, "Please report this problem to stomljen@yahoo.com\n");
        
        close_vbios(map);
        exit(2);
    }
#endif

    /*
     * check for others
     */

    if (map->chipset == CT_UNKWN) {
        fprintf(stderr, "Unknown chipset type and unrecognized bios.\n");
        fprintf(stderr, "915resolution only works with Intel 800/900 series graphic chipsets.\n");

        fprintf(stderr, "Chipset Id: %x\n", map->chipset_id);
        close_vbios(map);
        return 0;
    }

    /*
     * Figure out where the mode table is 
     */
    
    {
        address p = map->bios_ptr + 16;
        address limit = map->bios_ptr + VBIOS_SIZE - (3 * sizeof(vbios_mode));
        
        while (p < limit && map->mode_table == 0) {
            vbios_mode * mode_ptr = (vbios_mode *) p;
            
            if (((mode_ptr[0].mode & 0xf0) == 0x30) && ((mode_ptr[1].mode & 0xf0) == 0x30) &&
                ((mode_ptr[2].mode & 0xf0) == 0x30) && ((mode_ptr[3].mode & 0xf0) == 0x30)) {

                map->mode_table = mode_ptr;
            }
            
            p++;
        }

        if (map->mode_table == 0) {
            fprintf(stderr, "Unable to locate the mode table.\n");
            fprintf(stderr, "Please run the program 'dump_bios' as root and\n");
            fprintf(stderr, "email the file 'vbios.dmp' to stomljen@yahoo.com.\n");
            
            fprintf(stderr, "Chipset: %s\n", chipset_type_names[map->chipset]);
            close_vbios(map);
            return 0;
        }
    }

    /*
     * Determine size of mode table
     */
    
    {
        vbios_mode * mode_ptr = map->mode_table;
        
        while (mode_ptr->mode != 0xff) {
            map->mode_table_size++;
            mode_ptr++;
        }
    }

    /*
     * Figure out what type of bios we have
     *  order of detection is important
     */

    if (detect_bios_type(map, sizeof(vbios_modeline_type3))) {
        map->bios = BT_3;
    }
    else if (detect_bios_type(map, sizeof(vbios_modeline_type2))) {
        map->bios = BT_2;
    }
    else if (detect_bios_type(map, sizeof(vbios_resolution_type1))) {
        map->bios = BT_1;
    }
    else {
        fprintf(stderr, "Unable to determine bios type.\n");
        fprintf(stderr, "Please run the program 'dump_bios' as root and\n");
        fprintf(stderr, "email the file 'vbios.dmp' to stomljen@yahoo.com.\n");

        fprintf(stderr, "Chipset: %s\n", chipset_type_names[map->chipset]);
        fprintf(stderr, "Mode Table Offset: $C0000 + $%x\n", ((cardinal)map->mode_table) - ((cardinal)map->bios_ptr));
        fprintf(stderr, "Mode Table Entries: %u\n", map->mode_table_size);
        return 0;
    }

    return map;
}

static void close_vbios(vbios_map * map) {
    assert(!map->unlocked);

    FREE(map);
}

static void unlock_vbios(vbios_map * map) {

    assert(!map->unlocked);
        
    map->unlocked = TRUE;
    
    switch (map->chipset) {
    case CT_UNKWN:
        break;
    case CT_830:
    case CT_855GM:
        outl(0x8000005a, 0xcf8);
        map->b1 = inb(0xcfe);
        
        outl(0x8000005a, 0xcf8);
        outb(0x33, 0xcfe);
        break;
    case CT_845G:
    case CT_865G:
    case CT_915G:
    case CT_915GM:
    case CT_945G:
    case CT_945GM:
    case CT_945GME:
    case CT_946GZ:
    case CT_G965:
    case CT_Q965:
    case CT_965GM:
    case CT_G33:
    case CT_Q35:
    case CT_Q33:
    case CT_500GMA:
    case CT_GM45:
    case CT_GMA3150:
    case CT_HD3000:
        outl(0x80000090, 0xcf8);
        map->b1 = inb(0xcfd);
        map->b2 = inb(0xcfe);
        
        outl(0x80000090, 0xcf8);
        outb(0x33, 0xcfd);
        outb(0x33, 0xcfe);
        break;
    }

#if DEBUG
    {
        cardinal t = inl(0xcfc);
        printf("unlock PAM: (0x%08x)\n", t);
    }
#endif
}

static void relock_vbios(vbios_map * map) {

    assert(map->unlocked);
    map->unlocked = FALSE;
    
    switch (map->chipset) {
    case CT_UNKWN:
        break;
    case CT_830:
    case CT_855GM:
        outl(0x8000005a, 0xcf8);
        outb(map->b1, 0xcfe);
        break;
    case CT_845G:
    case CT_865G:
    case CT_915G:
    case CT_915GM:
    case CT_945G:
    case CT_945GM:
    case CT_945GME:
    case CT_946GZ:
    case CT_G965:
    case CT_Q965:
    case CT_965GM:
    case CT_G33:
    case CT_Q35:
    case CT_Q33:
    case CT_500GMA:
    case CT_GM45:
    case CT_GMA3150:
    case CT_HD3000:
        outl(0x80000090, 0xcf8);
        outb(map->b1, 0xcfd);
        outb(map->b2, 0xcfe);
        break;
    }

#if DEBUG
    {
        cardinal t = inl(0xcfc);
        printf("relock PAM: (0x%08x)\n", t);
    }
#endif
}


static void list_modes(vbios_map *map, cardinal raw) {
    cardinal i, x, y;

    for (i=0; i < map->mode_table_size; i++) {
        switch(map->bios) {
        case BT_1:
            {
                vbios_resolution_type1 * res = map_type1_resolution(map, map->mode_table[i].resolution);
                
                x = ((((cardinal) res->x2) & 0xf0) << 4) | res->x1;
                y = ((((cardinal) res->y2) & 0xf0) << 4) | res->y1;
                
                if (x != 0 && y != 0) {
                    printf("Mode %02x : %dx%d, %d bits/pixel\n", map->mode_table[i].mode, x, y, map->mode_table[i].bits_per_pixel);
                }

		if (raw)
		{
                    printf("Mode %02x (raw) :\n\t%02x %02x\n\t%02x\n\t%02x\n\t%02x\n\t%02x\n\t%02x\n\t%02x\n", map->mode_table[i].mode, res->unknow1[0],res->unknow1[1], res->x1,res->x_total,res->x2,res->y1,res->y_total,res->y2);
		}

            }
            break;
        case BT_2:
            {
                vbios_resolution_type2 * res = map_type2_resolution(map, map->mode_table[i].resolution);
                
                x = res->modelines[0].x1+1;
                y = res->modelines[0].y1+1;

                if (x != 0 && y != 0) {
                    printf("Mode %02x : %dx%d, %d bits/pixel\n", map->mode_table[i].mode, x, y, map->mode_table[i].bits_per_pixel);
                }
            }
            break;
        case BT_3:
            {
                vbios_resolution_type3 * res = map_type3_resolution(map, map->mode_table[i].resolution);
                
                x = res->modelines[0].x1+1;
                y = res->modelines[0].y1+1;
                
                if (x != 0 && y != 0) {
                    printf("Mode %02x : %dx%d, %d bits/pixel\n", map->mode_table[i].mode, x, y, map->mode_table[i].bits_per_pixel);
                }
            }
            break;
        case BT_UNKWN:
            break;
        }
    }
}

static void gtf_timings(int x, int y, int freq,
        unsigned long *clock,
        word *hsyncstart, word *hsyncend, word *hblank,
        word *vsyncstart, word *vsyncend, word *vblank)
{
    int hbl, vbl, vfreq;

    /*
      (y+1)/(20000.0/(11*freq) - 1) + 0.5
      = ((y+1) * (11*freq))/(20000.0 - (11*freq)) + 0.5
      = ((y+1) * (11*freq) + 10000.0 - (11*freq) / 2)/(20000.0 - (11*freq))
      = ((y+1) * (11*freq) + 10000.0 - 5 * freq - (freq + 1) / 2)/(20000.0 - (11*freq))
*/
    vbl = y + 1 +
      grub_divmod64 (((y+1) * (11*(long long)freq) + 10000 - 5 * (long long)freq
		      - (freq + 1) / 2),
		     (20000 - (11*(long long)freq)), 0);
    vfreq = vbl * freq;
    /*
      (x * (30.0 - 300000.0 / vfreq) /
      (70.0 + 300000.0 / vfreq) / 16.0 + 0.5)
      = ((x * (30.0 - 300000.0 / vfreq) /
          (70.0 + 300000.0 / vfreq) + 8) / 16)
      = ((x * (30.0 * vfreq - 300000.0) /
          (70.0 * vfreq + 300000.0) + 8) / 16)
      = (((x * (30 * vfreq - 300000)) /
          (70 * vfreq + 300000) + 8) / 16)
    */
    hbl = 16 * (int)((grub_divmod64((x * (30 * (long long)vfreq - 300000)),
				    (70 * (long long)vfreq + 300000), 0)
		      + 8) / 16);

    *vsyncstart = y;
    *vsyncend = y + 3;
    *vblank = vbl - 1;
    *hsyncstart = x + hbl / 2 - (x + hbl + 50) / 100 * 8 - 1;
    *hsyncend = x + hbl / 2 - 1;
    *hblank = x + hbl - 1;
    *clock = (x + hbl) * vfreq / 1000;
}

static void set_mode(vbios_map * map, cardinal mode, cardinal x, cardinal y, cardinal bp, cardinal htotal, cardinal vtotal) {
    int xprev, yprev;
    cardinal i, j;

    for (i=0; i < map->mode_table_size; i++) {
        if (map->mode_table[i].mode == mode) {
            switch(map->bios) {
            case BT_1:
                {
                    vbios_resolution_type1 * res = map_type1_resolution(map, map->mode_table[i].resolution);
                    
                    if (bp) {
                        map->mode_table[i].bits_per_pixel = bp;
                    }
                    
                    res->x2 = (htotal?(((htotal-x) >> 8) & 0x0f) : (res->x2 & 0x0f)) | ((x >> 4) & 0xf0);
                    res->x1 = (x & 0xff);
                    
                    res->y2 = (vtotal?(((vtotal-y) >> 8) & 0x0f) : (res->y2 & 0x0f)) | ((y >> 4) & 0xf0);
                    res->y1 = (y & 0xff);
		    if (htotal)
			res->x_total = ((htotal-x) & 0xff);

		    if (vtotal)
			res->y_total = ((vtotal-y) & 0xff);
                }
                break;
            case BT_2:
                {
                    vbios_resolution_type2 * res = map_type2_resolution(map, map->mode_table[i].resolution);

                    res->xchars = x / 8;
                    res->ychars = y / 16 - 1;
                    xprev = res->modelines[0].x1;
                    yprev = res->modelines[0].y1;

                    for(j=0; j < 3; j++) {
                        vbios_modeline_type2 * modeline = &res->modelines[j];
                        
                        if (modeline->x1 == xprev && modeline->y1 == yprev) {
                            unsigned long clock;
                            word hsyncstart, hsyncend, hblank;
                            word vsyncstart, vsyncend, vblank;

                            modeline->x1 = modeline->x2 = x-1;
                            modeline->y1 = modeline->y2 = y-1;

                            gtf_timings(x, y, freqs[j], &clock,
                                    &hsyncstart, &hsyncend, &hblank,
                                    &vsyncstart, &vsyncend, &vblank);
                            modeline->clock = clock;
                            modeline->hsyncstart = hsyncstart;
                            modeline->hsyncend = hsyncend;
                            modeline->hblank = hblank;
                            modeline->vsyncstart = vsyncstart;
                            modeline->vsyncend = vsyncend;
                            modeline->vblank = vblank;

                            if (htotal)
                                modeline->htotal = htotal;
                            else
                                modeline->htotal = modeline->hblank;

                            if (vtotal)
                                modeline->vtotal = vtotal;
                            else
                                modeline->vtotal = modeline->vblank;
                        }
                    }
                }
                break;
            case BT_3:
                {
                    vbios_resolution_type3 * res = map_type3_resolution(map, map->mode_table[i].resolution);
                    
                    xprev = res->modelines[0].x1;
                    yprev = res->modelines[0].y1;

                    for (j=0; j < 3; j++) {
                        vbios_modeline_type3 * modeline = &res->modelines[j];
                        
                        if (modeline->x1 == xprev && modeline->y1 == yprev) {
                            unsigned long clock;
                            word hsyncstart, hsyncend, hblank;
                            word vsyncstart, vsyncend, vblank;

                            modeline->x1 = modeline->x2 = x-1;
                            modeline->y1 = modeline->y2 = y-1;
                            
                            gtf_timings(x, y, freqs[j], &clock,
                                    &hsyncstart, &hsyncend, &hblank,
                                    &vsyncstart, &vsyncend, &vblank);
                            modeline->clock = clock;
                            modeline->hsyncstart = hsyncstart;
                            modeline->hsyncend = hsyncend;
                            modeline->hblank = hblank;
                            modeline->vsyncstart = vsyncstart;
                            modeline->vsyncend = vsyncend;
                            modeline->vblank = vblank;

                            if (htotal)
                                modeline->htotal = htotal;
                            else
                                modeline->htotal = modeline->hblank;
                            if (vtotal)
                                modeline->vtotal = vtotal;
                            else
                                modeline->vtotal = modeline->vblank;

                            modeline->timing_h   = y-1;
                            modeline->timing_v   = x-1;
                        }
                    }
                }
                break;
            case BT_UNKWN:
                break;
            }
        }
    }
}   

static void display_map_info(vbios_map * map) {
    printf("Chipset: %s\n", chipset_type_names[map->chipset]);
    printf("BIOS: %s\n", bios_type_names[map->bios]);

    printf("Mode Table Offset: $C0000 + $%x\n", ((cardinal)map->mode_table) - ((cardinal)map->bios_ptr));
    printf("Mode Table Entries: %u\n", map->mode_table_size);
}


static int parse_args(cardinal argc, char *argv[], chipset_type *forced_chipset,
		      cardinal *list, cardinal *mode, cardinal *x, cardinal *y,
		      cardinal *bp, cardinal *raw, cardinal *htotal,
		      cardinal *vtotal, cardinal *quiet) {
    cardinal index = 0;

    *list = *mode = *x = *y = *raw = *htotal = *vtotal = 0;
    *bp = 0;
    *quiet = 0;

    *forced_chipset = CT_UNKWN;

    if ((argc > index) && !strcmp(argv[index], "-q")) {
        *quiet = 1;
        index++;

        if(argc<=index) {
            return 0;
        }
    }    

    if ((argc > index) && !strcmp(argv[index], "-c")) {
        index++;

        if(argc<=index) {
            return 0;
        }
        
        if (!strcmp(argv[index], "845")) {
            *forced_chipset = CT_845G;
        }
        else if (!strcmp(argv[index], "855")) {
            *forced_chipset = CT_855GM;
        }
        else if (!strcmp(argv[index], "865")) {
            *forced_chipset = CT_865G;
        }
        else if (!strcmp(argv[index], "915G")) {
            *forced_chipset = CT_915G;
        }
        else if (!strcmp(argv[index], "915GM")) {
            *forced_chipset = CT_915GM;
        }
        else if (!strcmp(argv[index], "945G")) {
            *forced_chipset = CT_945G;
        }
        else if (!strcmp(argv[index], "945GM")) {
            *forced_chipset = CT_945GM;
        }
        else if (!strcmp(argv[index], "945GME")) {
            *forced_chipset = CT_945GME;
        }
        else if (!strcmp(argv[index], "946GZ")) {
            *forced_chipset = CT_946GZ;
        }
        else if (!strcmp(argv[index], "G965")) {
            *forced_chipset = CT_G965;
        }
        else if (!strcmp(argv[index], "Q965")) {
            *forced_chipset = CT_Q965;
        }
        else if (!strcmp(argv[index], "965GM")) {
            *forced_chipset = CT_965GM;
        }
        else if (!strcmp(argv[index], "G33")) {
            *forced_chipset = CT_G33;
        }
        else if (!strcmp(argv[index], "Q35")) {
            *forced_chipset = CT_Q35;
        }
        else if (!strcmp(argv[index], "Q33")) {
            *forced_chipset = CT_Q33;
        }
	else if (!strcmp(argv[index], "500GMA")) {
	    *forced_chipset = CT_500GMA;
	}
        else if (!strcmp(argv[index], "GM45")) {
            *forced_chipset = CT_GM45;
        }
        else if (!strcmp(argv[index], "GMA3150")) {
            *forced_chipset = CT_GMA3150;
        }
        else if (!strcmp(argv[index], "HD3000")) {
            *forced_chipset = CT_HD3000;
        }
        else {
            *forced_chipset = CT_UNKWN;
        }
        
        index++;
        
        if (argc<=index) {
            return 0;
        }
    }

    if ((argc > index) && !strcmp(argv[index], "-l")) {
        *list = 1;
        index++;

        if(argc<=index) {
            return 0;
        }
    }
    
    if ((argc > index) && !strcmp(argv[index], "-r")) {
        *raw = 1;
        index++;

        if(argc<=index) {
            return 0;
        }
    }
    
    if (argc-index < 3 || argc-index > 6) {
        return -1;
    }

    *mode = (cardinal) strtol(argv[index], NULL, 16);
    *x = (cardinal)atoi(argv[index+1]);
    *y = (cardinal)atoi(argv[index+2]);


    if (argc-index > 3) {
        *bp = (cardinal)atoi(argv[index+3]);
    }
    else {
        *bp = 0;
    }
    
    if (argc-index > 4) {
        *htotal = (cardinal)atoi(argv[index+4]);
    }
    else {
        *htotal = 0;
    }

    if (argc-index > 5) {
        *vtotal = (cardinal)atoi(argv[index+5]);
    }
    else {
        *vtotal = 0;
    }
    
    return 0;
}

static void usage(void) {
    printf("Usage: 915resolution [-q] [-c chipset] [-l] [mode X Y] [bits/pixel] [htotal] [vtotal]\n");
    printf("  Set the resolution to XxY for a video mode\n");
    printf("  Bits per pixel are optional.  htotal/vtotal settings are additionally optional.\n");
    printf("  Options:\n");
    printf("    -q don't show any normal messages\n");
    printf("    -c force chipset type (THIS IS USED FOR DEBUG PURPOSES)\n");
    printf("    -l display the modes found in the video BIOS\n");
    printf("    -r display the modes found in the video BIOS in raw mode (THIS IS USED FOR DEBUG PURPOSES)\n");
}

static int main_915 (int argc, char *argv[])
{
    vbios_map * map;
    cardinal list, mode, x, y, bp, raw, htotal, vtotal;
    cardinal quiet;
    chipset_type forced_chipset;
    
    if (parse_args(argc, argv, &forced_chipset, &list, &mode,
		   &x, &y, &bp, &raw, &htotal, &vtotal, &quiet) == -1) {
        printf("Intel 800/900 Series VBIOS Hack : version %s\n\n",
	       RES915_VERSION);
        usage();
        return 2;
    }

    if (!quiet)
      printf("Intel 800/900 Series VBIOS Hack : version %s\n\n",
	     RES915_VERSION);

    map = open_vbios(forced_chipset);
    if (!quiet)
      {
	display_map_info(map);
	printf("\n");
      }

    if (list) {
        list_modes(map, raw);
    }

    if (mode!=0 && x!=0 && y!=0) {
          unlock_vbios(map);

        set_mode(map, mode, x, y, bp, htotal, vtotal);

          relock_vbios(map);
        
        printf("Patch mode %02x to resolution %dx%d complete\n", mode, x, y);
        
        if (list) {
            list_modes(map, raw);
        }
    }

    close_vbios(map);
    
    return 0;
}





static grub_err_t
grub_cmd_915resolution (grub_command_t cmd __attribute__ ((unused)), 
			int argc, char *argv[])
{
  return main_915 (argc, argv);
}

static grub_command_t cmd;

GRUB_MOD_INIT(915resolution)
{
  cmd = grub_register_command ("915resolution", grub_cmd_915resolution,
			       "915resolution", "Intel VBE editor");
}

GRUB_MOD_FINI(915resolution)
{
  grub_unregister_command (cmd);
}
