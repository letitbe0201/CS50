#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>

typedef uint8_t BYTE;

int main(int argc, char *argv[])
{
    //validate the input
    if (argc != 2)
    {
        fprintf(stderr, "Usage: ./recover image\n");
        return 1;
    }

    //open the infile
    char *infile = argv[1];
    FILE *inptr = fopen(infile, "r");
    //initialize the outfile name
    char outfile[8];
    FILE *img = NULL;

    //make sure the file exists
    if (inptr == NULL)
    {
        fprintf(stderr, "the file can't be open\n");
        return 2;
    }

    //make a first buffer for test
    BYTE *buffer0 = malloc(sizeof(BYTE) * 512);

    //read a block from the file
    int count = fread(buffer0, sizeof(BYTE), 512, inptr);

    //check if the first block suffice 512B
    if (count != 512)
    {
        fprintf(stderr, "the file is not even 1 block(512B)!\n");
        return 1;
    }

    //move the pointer back
    fseek(inptr, -(sizeof(BYTE) * 512), SEEK_CUR);

    //the job of buffer0 is finish
    free(buffer0);

    //count for JPEGs
    int jpegNum = 0;
    //int* numJpeg = &jpegNum;

    //repeat until end of file(< 512B)
    while (count == 512)
    {
        //allocate a buffer for fread
        BYTE *buffer = malloc(sizeof(BYTE) * 512);

        //read a block from the file
        count = fread(buffer, sizeof(BYTE), 512, inptr);

        //validate the first four byte
        if (buffer[0] == 0xff && buffer[1] == 0xd8 && buffer[2] == 0xff && (buffer[3] & 0xf0) == 0xe0 && count == 512)
        {
            //if it's the first jpeg then skip this step
            if (jpegNum != 0)
            {
                //close previous image
                fclose(img);
            }

            //issue with the file name of JPEG
            jpegNum += 1;
            sprintf(outfile, "%03i.jpg", jpegNum - 1);
            img = fopen(outfile, "w");

            //write the block into the outfile
            fwrite(buffer, sizeof(BYTE), 512, img);
        }
        else
        {
            //identify if the first jpeg is found or not
            if ((jpegNum != 0) && (count == 512))
            {
                //write the block into the outfile
                fwrite(buffer, sizeof(BYTE), 512, img);
            }
        }

        //free the dynamic memory of buffer
        free(buffer);

    }

    //close the last img
    fclose(img);

    //close the input file
    fclose(inptr);

    //successfully execute
    return 0;
}
