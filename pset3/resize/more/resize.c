// RESIZE a BMP file

#include <stdio.h>
#include <stdlib.h>
#include <math.h>

#include "bmp.h"

int main(int argc, char *argv[])
{
    // ensure proper usage
    if (argc != 4)
    {
        fprintf(stderr, "Usage: ./resize f infile outfile\n");
        return 1;
    }

    // remember filenames
    char *infile = argv[2];
    char *outfile = argv[3];

    // open input file
    FILE *inptr = fopen(infile, "r");
    if (inptr == NULL)
    {
        fprintf(stderr, "Could not open %s.\n", infile);
        return 2;
    }

    // open output file
    FILE *outptr = fopen(outfile, "w");
    if (outptr == NULL)
    {
        fclose(inptr);
        fprintf(stderr, "Could not create %s.\n", outfile);
        return 3;
    }

    ////issue the resize number
    float resizeNum = atof(argv[1]);
    if (resizeNum <= 0 || resizeNum > 100)
    {
        fprintf(stderr, "Please enter a number between 0.0 - 100.0\n");
        return 1;
    }
    ////reciprocal of resize factor
    float magicNum = 1 / resizeNum;

    // read infile's BITMAPFILEHEADER
    BITMAPFILEHEADER bf;
    fread(&bf, sizeof(BITMAPFILEHEADER), 1, inptr);

    // read infile's BITMAPINFOHEADER
    BITMAPINFOHEADER bi;
    fread(&bi, sizeof(BITMAPINFOHEADER), 1, inptr);

    // ensure infile is (likely) a 24-bit uncompressed BMP 4.0
    if (bf.bfType != 0x4d42 || bf.bfOffBits != 54 || bi.biSize != 40 ||
        bi.biBitCount != 24 || bi.biCompression != 0)
    {
        fclose(outptr);
        fclose(inptr);
        fprintf(stderr, "Unsupported file format.\n");
        return 4;
    }

    ////restore the original and new biWidth, biHeight
    BITMAPFILEHEADER bfNew = bf;
    BITMAPINFOHEADER biNew = bi;

    biNew.biWidth = bi.biWidth * resizeNum;
    biNew.biHeight = bi.biHeight * resizeNum;
    ////test
    //printf("%d\n", bi.biHeight);
    //printf("%d\n", biNew.biHeight);

    ////make sure the new width and height won't exceed the type LONG in bmp.h
    if (biNew.biWidth > ((2 ^ 32) - 1) || biNew.biHeight > ((2 ^ 32) - 1) || biNew.biWidth < 1)
    {
        fprintf(stderr, "Can't handle this!\n");
        return 1;
    }

    // determine paddings for scanlines
    int oriPadding = (4 - (bi.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;
    int newPadding = (4 - (biNew.biWidth * sizeof(RGBTRIPLE)) % 4) % 4;

    ////determine the new biSizeImage
    biNew.biSizeImage = ((sizeof(RGBTRIPLE) * biNew.biWidth) + newPadding) * abs(biNew.biHeight);

    ////determine the new biSize
    bfNew.bfSize = biNew.biSizeImage + sizeof(BITMAPFILEHEADER) + sizeof(BITMAPINFOHEADER);

    ///////////////////test
    //printf("%d\n", bf.bfType);
    //printf("%d\n", bfNew.bfType);

    // write outfile's BITMAPFILEHEADER
    fwrite(&bfNew, sizeof(BITMAPFILEHEADER), 1, outptr);

    // write outfile's BITMAPINFOHEADER
    fwrite(&biNew, sizeof(BITMAPINFOHEADER), 1, outptr);

    ////////// iterate over columns of output picture
    for (int i = 0, biNewHeight = abs(biNew.biHeight); i < biNewHeight; i++)
    {
        ////determine which column to copy from the original picture with (1/factor * i)
        int indexHeight = magicNum * i;
        int nextIndexHeight = magicNum * (i + 1);
        ////determine the distance should the file pointer move
        int move;

        ////read one row of input file
        RGBTRIPLE *rowOfInput = malloc(sizeof(RGBTRIPLE) * bi.biWidth);
        fread(rowOfInput, sizeof(RGBTRIPLE), bi.biWidth, inptr);

        ////try to figure out where the pointer should be in the infile for next row to copy
        if (nextIndexHeight == indexHeight)
        {
            ////in order to copy the same row, the pointer should move backward
            int *p = &move;
            *p = -(sizeof(RGBTRIPLE) * bi.biWidth);
        }
        else
        {
            ////to copy the next XX row (include paddings)
            int *p = &move;
            *p = (oriPadding * (nextIndexHeight - indexHeight) + (sizeof(RGBTRIPLE) * bi.biWidth) * (nextIndexHeight - indexHeight - 1));
        }

        //// move to the next position of copying
        fseek(inptr, move, SEEK_CUR);

        // iterate over rows of output picture
        for (int j = 0; j < biNew.biWidth; j++)
        {
            ////look for what index we are going to pick from infile
            int indexWidth = magicNum * j;

            //// create a dynamic memory for temporary storage
            RGBTRIPLE *triple = malloc(sizeof(RGBTRIPLE));
            //RGBTRIPLE triple;

            ////copy the chosen infile pixel to the outfile
            *triple = rowOfInput[indexWidth];

            // write RGB triple to outfile
            fwrite(triple, sizeof(RGBTRIPLE), 1, outptr);

            free(triple);
        }

        // add it back (to demonstrate how)
        for (int k = 0; k < newPadding; k++)
        {
            fputc(0x00, outptr);
        }

        ////free storage of current infile row
        free(rowOfInput);
    }

    // close infile
    fclose(inptr);

    // close outfile
    fclose(outptr);

    // success
    return 0;
}