
> ## Notice of potentially breaking change
>
> As of v0.10.4, core-js is no longer included with jimp or its extensions. If you rely on core-js, install it with either `yarn add core-js` or `npm i core-js`

## Tools

:hammer: [cli](./packages/cli) - Jimp as a CLI program. Can load and run all plugins

## Image Manipulation Methods (Default Plugins)

- [blit](./packages/plugin-blit) - Blit an image onto another.
- [blur](./packages/plugin-blur) - Quickly blur an image.
- [color](./packages/plugin-color) - Various color manipulation methods.
- [contain](./packages/plugin-contain) - Contain an image within a height and width.
- [cover](./packages/plugin-cover) - Scale the image so the given width and height keeping the aspect ratio.
- [displace](./packages/plugin-displace) - Displaces the image based on a displacement map
- [dither](./packages/plugin-dither) - Apply a dither effect to an image.
- [flip](./packages/plugin-flip) - Flip an image along it's x or y axis.
- [gaussian](./packages/plugin-gaussian) - Hardcore blur.
- [invert](./packages/plugin-invert) - Invert an images colors
- [mask](./packages/plugin-mask) - Mask one image with another.
- [normalize](./packages/plugin-normalize) - Normalize the colors in an image
- [print](./packages/plugin-print) - Print text onto an image
- [resize](./packages/plugin-resize) - Resize an image.
- [rotate](./packages/plugin-rotate) - Rotate an image.
- [scale](./packages/plugin-scale) - Uniformly scales the image by a factor.

## Extra Plugins

- [circle](./packages/plugin-circle) - Creates a circle out of an image.
- [shadow](./packages/plugin-shadow) - Creates a shadow on an image.
- [fisheye](./packages/plugin-fisheye) - Apply a fisheye effect to an image.
- [threshold](./packages/plugin-threshold) - Lighten an image. Good for scanned drawing and signatures.

:rocket: If you want to add your plugins to this list make a PR! :rocket:

## Custom Jimp

If you want to extend jimp or omit types or functions visit [@jimp/custom](./packages/custom).

- Add file-types or switch encoder/decoders
- Add add/remove plugins (image manipulation methods)

## Contributing

Basically clone, change, test, push and pull request.

Please read the [CONTRIBUTING documentation](CONTRIBUTING.md).

## License

Jimp is licensed under the MIT license. Open Sans is licensed under the Apache license

## Project Using Jimp

