const VIEW_BOX_OFFSET = 60;
const VIEW_BOX_OFFSET_HALF = VIEW_BOX_OFFSET / 2;

function canvasTintImage(image, color) {
  const canvas = document.createElement('canvas');
  const context = canvas.getContext('2d');

  context.canvas.width = image.width;
  context.canvas.height = image.height;

  context.save();
  context.fillStyle = color;
  context.fillRect(0, 0, context.canvas.width, context.canvas.height);
  context.globalCompositeOperation = "destination-atop";
  context.globalAlpha = 1;
  context.drawImage(image, 0, 0);
  context.restore();

  return context.canvas;
}

function getViewBox(viewBox) {
  viewBox.height += VIEW_BOX_OFFSET;
  viewBox.h += VIEW_BOX_OFFSET;
  viewBox.width += VIEW_BOX_OFFSET;
  viewBox.w += VIEW_BOX_OFFSET;
  viewBox.x -= VIEW_BOX_OFFSET_HALF;
  viewBox.x2 += VIEW_BOX_OFFSET_HALF;
  viewBox.y -= VIEW_BOX_OFFSET_HALF;
  viewBox.y2 += VIEW_BOX_OFFSET_HALF;

  return viewBox;
}

function loadImage(urlPath, force = false) {
  let canceled = false;
  let imgPath = urlPath;

  const img = new Image();

  return Object.assign(new Promise(async (res, rej) => {
    try {
      img.onload = () => {
        img.onerror = null;
        img.onload = null;

        URL.revokeObjectURL(imgPath);

        return res(img);
      };

      img.onerror = (err) => {
        img.onload = null;
        img.onerror = null;

        URL.revokeObjectURL(imgPath);

        let curErr;

        if (canceled) {
          curErr = new Error('Image downloading has been canceled');

          curErr.canceled = true;
        } else {
          curErr = new Error('Couldn\'t load the image');
        }

        curErr.event = err;

        rej(curErr);
      };

      img.src = imgPath;
    } catch (err) {
      err.url = imgPath;

      rej(err);
    }
  }), {
    cancel() {
      if (!canceled) {
        img.src = '';
        canceled = true;
      }

      return this;
    },
  });
}

async function base64BitmapToRaw(srcBitmap) {
  const decodedStr = self.atob(srcBitmap); // eslint-disable-line no-restricted-globals
  let result;

  if (srcBitmap.startsWith('eJ')) {
    result = pako.inflate(decodedStr);
  } else {
    result = Uint8Array.from(decodedStr, c => c.charCodeAt(0));
  }

  return result;
}

function getBBoxSize(bbox) {
  return {
    width: bbox[1][0] - bbox[0][0],
    height: bbox[1][1] - bbox[0][1],
  };
}

Vue.component('smarttool-editor', {
  template: `
    <div v-loading="loading">
      <svg ref="container" xmlns="http://www.w3.org/2000/svg" version="1.1" xmlns:xlink="http://www.w3.org/1999/xlink" width="100%" height="100%"></svg>
    </div>
  `,
  props: {
    maskOpacity: 0.5,
    bbox: {
      type: Array,
      required: false,
    },
    imageUrl: {
      type: String,
      required: true,
    },
    mask: {
      type: Object,
    },
  },
  data() {
    return {
      pt: null,
      container: null,
      loading: true,
      contours: [],
    };
  },
  watch: {
    imageUrl() {
      console.log('image url was changed')
      // this.methods.init()
      this.group.clear()
      this.backgroundEl = this.sceneEl.image(this.imageUrl).loaded(() => {
        const viewBox = this.sceneEl.bbox();
        this.sceneEl.viewbox(viewBox)
        this.loading = false;
      });
      this.group.add(
        this.backgroundEl,
        this.bboxEl
      );
    },

    'mask.contour': {
      handler() {
        this.contours.forEach((c) => {
          c.remove();
        });

        if (this.mask?.contour) {
          this.mask?.contour.forEach((c) => {
            const contourEl1 = this.sceneEl.polygon()
              .plot(c || [])
              .fill('none')
              .stroke({
                color: 'white',
                width: 3,
              });
            const contourEl2 = this.sceneEl.polygon()
              .plot(c || [])
              .fill('none')
              .stroke({
                color: '#ff6600',
                width: 3,
                dasharray: '10 10',
              });

            this.contours.push(contourEl1, contourEl2);
          });
        }
      },
      deep: true,
    },
    mask: {
      async handler() {
        if (!this.mask) {
          if (this.maskEl) {
            this.maskEl.load('data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7');
          }
          return;
        };
        const buf = await base64BitmapToRaw(this.mask.data);
        const annImageUrl = URL.createObjectURL(new Blob([buf]));
        let image = await loadImage(annImageUrl);
        const canvasImg = canvasTintImage(image, this.mask.color);

        this.maskEl.load(canvasImg.toDataURL())
          .attr({
            width: image.width,
            height: image.height,
          })
          .move(...this.mask.origin);
      },
      deep: true,
      immediate: true
    },

    bbox() {
      console.log(this.bbox)
      if (!this.bbox) {
        console.log("deleting bboxEl")
        this.bboxEl.style.display = "none";
        console.log(this.bboxEl)
        return
      }

      const bboxSize = getBBoxSize(this.bbox);

      if (!this.bboxEl) {
        this.bboxEl = this.sceneEl
          .rect(bboxSize.width, bboxSize.height)
          .move(this.bbox[0][0], this.bbox[0][1])
          .selectize()
          .resize()
          .attr({
            "fill-opacity": 0,
          })
          .on('resizedone', () => {
            const x = this.bboxEl.x();
            const y = this.bboxEl.y();
            const w = this.bboxEl.width();
            const h = this.bboxEl.height();
            this.$emit('update:bbox', [[x, y], [x + w, y + h]]);
          });
      }

      this.bboxEl.size(bboxSize.width, bboxSize.height)
        .move(this.bbox[0][0], this.bbox[0][1])

      this.sceneEl.viewbox(getViewBox(this.bboxEl.bbox()))
    },

    maskOpacity: {
      handler() {
        if (!this.maskEl) return;
        this.maskEl.node.style.opacity = this.maskOpacity;
      },
      immediate: true,
    },
  },
  methods: {

    init() {
      this.container.addEventListener('contextmenu', (e) => {
        e.preventDefault();
      });

      this.sceneEl = SVG(this.container)
        .panZoom({
          zoomMin: 0.1,
          zoomMax: 20,
          panButton: 2
        });

      this.group = this.sceneEl.group();

      this.maskEl = this.sceneEl.image();
      this.maskEl.addClass('sly-smart-tool__annotation');
      this.maskEl.node.style.opacity = this.maskOpacity;

      if (this.mask?.contour) {
        this.mask?.contour.forEach((c) => {
          const contourEl1 = this.sceneEl.polygon()
            .plot(c || [])
            .fill('none')
            .stroke({
              width: 3,
              color: '#ff6600',
              // dasharray: '10 10',
            });
          const contourEl2 = this.sceneEl.polygon()
            .plot(c || [])
            .fill('none')
            .stroke({
              color: 'white',
              width: 3,
              dasharray: '10 10',
            });

          this.contours.push(contourEl1, contourEl2);
        });
      }

      if (this.bbox) {
        const bboxSize = getBBoxSize(this.bbox);

        this.bboxEl = this.sceneEl
          .rect(bboxSize.width, bboxSize.height)
          .move(this.bbox[0][0], this.bbox[0][1])
          .selectize()
          .resize()
          .attr({
            "fill-opacity": 0,
          })
          .on('resizedone', () => {
            const x = this.bboxEl.x();
            const y = this.bboxEl.y();
            const w = this.bboxEl.width();
            const h = this.bboxEl.height();
            this.$emit('update:bbox', [[x, y], [x + w, y + h]]);
          });
      }


      this.backgroundEl = this.sceneEl.image(this.imageUrl).loaded(() => {
        this.loading = false;
        const viewBox = this.sceneEl.bbox();
        this.sceneEl.viewbox(viewBox)
      });

      this.group.add(this.backgroundEl, this.maskEl, this.bboxEl);

      // this.bboxEl.on('contextmenu', this.pointHandler);
    },

  },

  mounted() {
    this.container = this.$refs['container'];

    this.init();
  }
});