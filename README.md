# Python Image Filters
This repositor contains image filters I programmed using python. As I'm writing this the 2 Image filters in the repository are an Ordered Dithering filter, and 2 Variations of the Kuwahara filter.

## Ordered Dithering

Ordered Dithering is a process which first adds a noise to an image and then quantizes the color to lower the color depth. The noise added to the image is very specifically made to cause quantization in different directions in a ratio relative to the original colors closeness to each color.
This leads to an effect similar to how the RGB sub pixels work in a monitor where when looking at the image from a distance is seems like the color is an imtermadiate but when zooming the the quantization can be seen.

**Before Dithering**
<img src="https://github.com/Sea-Bastion/PyImageFilters/blob/main/Dithering/resources/lighthouse.png" width="200">
**After Dithering**
<img src="https://github.com/Sea-Bastion/PyImageFilters/blob/main/Dithering/resources/Ditherhouse.png" width="200">


## Kuwahara

The Kuwahara Filter is an interesting filter. The filter samples the standard deviation of the pixel colors in 8 directions and uses the standard deviation to weight blurring in each direction favoring directions with lower StDev. This causes blurring in directions away from large color changes and this effect in general conserves edges when blurring. 
Overall the filter gives a very painterly look merging nearby similar colors into one bloch similar to a stroak of paint. 

A modification of the Kuwahara filter called the Anisotropic Kuwahara filter uses image structure tensor eigen values data to squash and stretch the window of the blur with the visual direction of the image leading to more natural shapes to the "brush strokes".

**Before Kuwahara**
<img src="https://github.com/Sea-Bastion/PyImageFilters/blob/main/Kuwahara/resources/monkey.jpg" width="200">
**After Kuwahara**
<img src="https://github.com/Sea-Bastion/PyImageFilters/blob/main/Kuwahara/resources/MonkeyOut.jpg" width="200">
