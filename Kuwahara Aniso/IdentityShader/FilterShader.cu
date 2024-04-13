 
#include <cuda_runtime.h>
// https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#texture-functions

extern "C"
__global__ void Kuwahara(cudaTextureObject_t Image, int *ImageShape, float *Mask, int MaskSize, unsigned char *OutImage){


//	int MaskRadius = MaskSize/2;

	int y = blockIdx.x;
	int x = threadIdx.x;
	
	int CenterIndex = y * ImageShape[1] + x;
	CenterIndex *= 4;

	uchar4 PixelData = tex2D<uchar4>(Image, x, y);

	printf ("%.3f\n ", (float)PixelData.x );
	OutImage[CenterIndex + 0] = PixelData.x;
	OutImage[CenterIndex + 1] = PixelData.y;
	OutImage[CenterIndex + 2] = PixelData.z;
	OutImage[CenterIndex + 3] = 1;


}


__global__ void BoxBlur(double *buffer, int filter_size, double *return_value){

	double sum = 0;

	for (int y = 0; y <filter_size ;y++){
		sum += buffer[y];
	}

	sum /= filter_size;
	return_value[0] = sum;


}
