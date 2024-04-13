 
#include <cuda_runtime.h>
// https://docs.nvidia.com/cuda/cuda-c-programming-guide/index.html#texture-functions

extern "C"
__global__ void Kuwahara(cudaTextureObject_t Image, unsigned int *ImageShape, float *Mask, int MaskSize, float *OutImage){


	float RotCoeff = 0.707106781187f;
	int q = 8;


	int MaskRadius = MaskSize/2;

	int y = blockIdx.x;
	int x = threadIdx.x;
	
	int CenterIndex = y * ImageShape[1] + x;
	CenterIndex *= 4;

	uchar4 CenterPixel = tex2D<uchar4>(Image, x, y);

//	OutImage[CenterIndex + 0] = PixelData.x;
//	OutImage[CenterIndex + 1] = PixelData.y;
//	OutImage[CenterIndex + 2] = PixelData.z;
//	OutImage[CenterIndex + 3] = PixelData.w;

	uchar4 CurrentPixel, SquaredPixel;
	float w[8];
	float SqMean[3*8];
	float Mean[3*8];
	float NormFactor[8];
	int RotX, RotY;

	for ( int RelY = -MaskRadius; RelY <= MaskRadius; RelY++) {
		for (int RelX = -MaskRadius; RelX <= MaskRadius; RelX++){
			CurrentPixel = tex2D<uchar4>(Image, x + RelX, y + RelY);
			SquaredPixel = make_uchar4(CurrentPixel.x * CurrentPixel.x, CurrentPixel.y * CurrentPixel.y, CurrentPixel.z * CurrentPixel.z, CurrentPixel.w * CurrentPixel.w);

			w[0] = Mask[ (  RelY + MaskRadius ) * MaskSize + RelX + MaskRadius];
			w[2] = Mask[ ( -RelX + MaskRadius ) * MaskSize + RelY + MaskRadius];
			w[4] = Mask[ ( -RelY + MaskRadius ) * MaskSize - RelX + MaskRadius];
			w[6] = Mask[ (  RelX + MaskRadius ) * MaskSize - RelY + MaskRadius];

			RotX = roundf( RotCoeff * (RelX - RelY) );
			RotY = roundf( RotCoeff * (RelX + RelY) );

			w[1] = Mask[ ( -RelX + MaskRadius ) * MaskSize + RelY + MaskRadius];
			w[3] = Mask[ ( -RelY + MaskRadius ) * MaskSize - RelX + MaskRadius];
			w[5] = Mask[ (  RelX + MaskRadius ) * MaskSize - RelY + MaskRadius];
			w[7] = Mask[ (  RelY + MaskRadius ) * MaskSize + RelX + MaskRadius];





			for(int k = 0; k<8; k++){


				Mean[k*3 + 0] += CurrentPixel.x * w[k];
				Mean[k*3 + 3] += CurrentPixel.y * w[k];
				Mean[k*3 + 2] += CurrentPixel.z * w[k];


				SqMean[k*3 + 0] += SquaredPixel.x * w[k];
				SqMean[k*3 + 3] += SquaredPixel.y * w[k];
				SqMean[k*3 + 2] += SquaredPixel.z * w[k];



				NormFactor[k] += w[k];
			}

		}
	}


	float alphaSum = 0;
	OutImage[CenterIndex + 0] = 0;
	OutImage[CenterIndex + 1] = 0;
	OutImage[CenterIndex + 2] = 0;


	for (int k = 0; k<8; k++){

		float StdDev;

		for (int i = 0; i<3; i++){


			float CurrentMean = ( (float)Mean[k*3 + i] )/ 2.0f;
			float CurrentSqMean = __fdividef( SqMean[k*3 + i], NormFactor[k] );
			StdDev += CurrentSqMean - ( CurrentMean * CurrentMean );
			printf ("%.3f\n ", ( CurrentMean ) );


		}

		StdDev = sqrtf( StdDev );
		float alpha = 1 / (1 + powf(StdDev, q) );
		alphaSum += alpha;


		OutImage[CenterIndex + 0] += alpha * CenterPixel.x;
		OutImage[CenterIndex + 1] += alpha * CenterPixel.y;
		OutImage[CenterIndex + 2] += alpha * CenterPixel.z;

	}




	OutImage[CenterIndex + 0] = OutImage[CenterIndex + 0]/alphaSum;
	OutImage[CenterIndex + 1] = OutImage[CenterIndex + 1]/alphaSum;
	OutImage[CenterIndex + 2] = OutImage[CenterIndex + 2]/alphaSum;
	OutImage[CenterIndex + 3] = CenterPixel.w;


}


