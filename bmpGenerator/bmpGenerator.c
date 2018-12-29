/* * BMP GENERATOR *
 * The generated BMP image will have dimensions DRAW_WIDTH x DRAW_HEIGHT.
 * Use the pixelColor function to define the color at any given (x, y) coordinate.
 * To use your own colors in the BMP, update the color array and change COLORS to match the length of the array.
 */

#include <errno.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define COLORS 16
#define DRAW_WIDTH 400
#define DRAW_HEIGHT 400

#define FILE_HEADER_SIZE 14
#define INFO_HEADER_SIZE 40
#define HEADER_SIZE (FILE_HEADER_SIZE + INFO_HEADER_SIZE)
#define PALETTE_SIZE (COLORS * 4)
#define METADATA_SIZE (HEADER_SIZE + PALETTE_SIZE)
#define MAX_PIXEL_DATA_SIZE ((DRAW_WIDTH + 1) * 2 * DRAW_HEIGHT)

// 72 DPI × 39.3701 inches per meter yields 2834.6472
#define RESOLUTION 2835

const char *filename = "img.bmp";

const int color[COLORS] = {
	0xFF0000, // RED : 0
	0x8B0000, // DARKRED : 1
	0xFFA500, // ORANGE : 2
	0xFFC0CB, // PINK : 3
	0xFFFF00, // YELLOW : 4
	0x00FF00, // LIME : 5
	0x008000, // GREEN : 6
	0x8FBC8F, // DARK_SEA_GREEN : 7
	0x00FFFF, // CYAN : 8
	0x000080, // NAVY : 9
	0x800080, // PURPLE : 10
	0xFF00FF, // MAGENTA : 11
	0xD2691E, // CHOCOLATE : 12
	0x708090, // SLATE_GRAY : 13
	0x000000, // BLACK : 14
	0xFFFFFF, // WHITE : 15
};

// Describes the color found at any given (x, y) coordinate.
// The returned value corresponds to an index of the color array.
int pixelColor(int x, int y);

// Generate the bytes for the pixel data.
char* createPixelData(int* pixelDataSize);

// Generate the bytes for the metadata: file header, info header, and color palette.
char* createMetadata(int pixelDataSize);

// Write an int into the first 4 bytes of a char array with little endian format.
void writeInt(char *dest, int num);

int main() {
	// open the file for write
	FILE* fp = fopen(filename, "w");
	if (!fp) {
		printf("ERROR: %s\n", strerror(errno));
	}
	
	// generate the BMP data
	int pixelDataSize;
	char* pixelData = createPixelData(&pixelDataSize);
	char* metadata = createMetadata(pixelDataSize);

	// write the BMP data to the file
	for (int i = 0; i < METADATA_SIZE; i++) {
		fputc(metadata[i], fp);
	}
	
	for (int i = 0; i < pixelDataSize; i++) {
		fputc(pixelData[i], fp);
	}
	
	// cleanup
	fclose(fp);
	free(pixelData);
	free(metadata);
}

int pixelColor(int x, int y) {
	return ((x + y) / 8) % COLORS;
}

char* createPixelData(int* pixelDataSize) {
	char* pixelData = (char*)malloc(MAX_PIXEL_DATA_SIZE);
	char runColor;
	char nextColor;
	int run = 1;
	int i = 0;
	
	for (int y = DRAW_HEIGHT - 1; y >= 0; y--) {
		runColor = pixelColor(0, y);
		run = 1;
		
		for (int x = 1; x < DRAW_WIDTH; x++) {
			nextColor = pixelColor(x, y);
			
			if (nextColor == runColor) {
				// the max run length is 255 with 8-bit/pixel RLE compression
				if (run == 255) {
					pixelData[i++] = run;
					pixelData[i++] = runColor;
					run = 1;
				} else {
					run++;
				}
			} else {
				pixelData[i++] = run;
				pixelData[i++] = runColor;
				runColor = nextColor;
				run = 1;
			}
		}
		
		pixelData[i++] = run;
		pixelData[i++] = runColor;
		pixelData[i++] = 0;
		
		if (y == 0) {
			// end of bitmap
			pixelData[i++] = 1;
		} else {
			// end of line
			pixelData[i++] = 0;
		}
	}
	
	*pixelDataSize = i;
	return pixelData;
}

char* createMetadata(int pixelDataSize) {
	char* header = (char*)calloc(METADATA_SIZE, sizeof(char));
	char* palette = header + HEADER_SIZE;

	/** FILE HEADER **/
	// bitmap signature [bytes 0-1]
	header[0] = 'B';
	header[1] = 'M';
	// file size [bytes 2-5]
	writeInt(header+2, pixelDataSize + METADATA_SIZE);
	// offset of pixel data inside the image [bytes 10-13]
	writeInt(header+10, HEADER_SIZE);
	
	/** INFO HEADER **/
	// info header size [bytes 14-17]
	writeInt(header+14, INFO_HEADER_SIZE);
	// width of the image [bytes 18-21]
	writeInt(header+18, DRAW_WIDTH);
	// height of the image [bytes 22-25]
	writeInt(header+22, DRAW_HEIGHT);
	// planes [bytes 26-27]
	header[26] = 1;
	// bits per pixel [bytes 28-29]
	header[28] = 8;
	// compression method (8-bit/pixel RLE) [bytes 30-33]
	writeInt(header+30, 1);
	// size of pixel data [bytes 34-37]
	writeInt(header+34, pixelDataSize);
    // horizontal resolution in pixels per meter [bytes 38-41]
	writeInt(header+38, RESOLUTION);
    // vertical resolution in pixels per meter [bytes 42-45]
	writeInt(header+42, RESOLUTION);
	// color pallette information [bytes 46-49]
	writeInt(header+46, COLORS);
	
	/** COLOR PALETTE **/
	for (int i = 0; i < COLORS; i++) {
		writeInt(palette + i*4, color[i]);
	}
	
	return header;
}

void writeInt(char *dest, int num) {
	for (int i = 0; i < 4; i++) {
		dest[i] = (num>>(i*8))%256;
	}
}
