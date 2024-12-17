Vue.component('sly-py-labeled-image', {
  props: ['imgUrl', 'projectMeta', 'annotation', 'options', 'visibleClasses'],
  data() {
    return {
      imageWidgetState: null,
      imageWidgetStyles: {
        width: '100%',
        height: '300px',
      }
    };
  },
  methods: {
    imageLoaded(imageInfo) {
      console.log("asdasd", imageInfo.width, imageInfo.height)
      const { width: maxWidth } = this.$el.getBoundingClientRect();
      const ratio = maxWidth / imageInfo.width;
      const height = `${Math.max(Math.floor(imageInfo.height * ratio), 100)}px`;
      this.imageWidgetStyles.height = height;
    },
  },
  mounted() {
    console.log("++++")
  },
  template: `
<div class="sly-py-labeled-image" style="position: relative;">
  <div class="fflex">
    <el-button @click="imageWidgetState.fitImage()" type="text"><i class="zmdi zmdi-aspect-ratio-alt mr5"></i>Reset zoom</el-button>
    <el-slider
      :min="0"
      :max="1"
      :step="0.1"
      style="width: 150px; margin-left: 30px;"
      v-model="options.opacity"
    ></el-slider>
  </div>
  <sly-img
    @exposed="imageWidgetState = $event"
    :style="imageWidgetStyles"
    :image-url="imgUrl"
    :project-meta="projectMeta"
    :annotation="annotation"
    :options="options"
    @image-info="imageLoaded"
  />
</div>
  `,
});