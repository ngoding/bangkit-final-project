<template>
  <div class="bangkit">
    <h1>Hello world!</h1>
    <h3 v-if="!this.model">
      Loading model
    </h3>
    <pulse-loader v-if="!this.model" size="10px"/>
    <div class="webcam">
      <video id="video" width="100%" height="100%" autoplay muted playsinline/>
      <p id="webcamPredictions">{{this.result}}</p>
    </div>
  </div>
</template>

<script>
// import * as tf from '@tensorflow/tfjs';
import Vue from 'vue'
import AsyncComputed from 'vue-async-computed'
import * as mobilenet from '@tensorflow-models/mobilenet';
import PulseLoader from 'vue-spinner/src/PulseLoader.vue'

Vue.use(AsyncComputed)

export default {
  name: 'Bangkit',
  components: {
    PulseLoader
  },
  computed: {
    video () {
      return document.getElementById('video')
    },
  },
  data () {
    return {
      model: null,
      loadingModel: false,
      result: null
    }
  },
  methods: {
    async startVideo () {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {}
      })
      this.video.srcObject = stream
    },
    async loadModel () {
      // const mobilenet = require('@tensorflow-models/mobilenet');
      // this.model = await tf.loadGraphModel('/model.json')
      this.model = await mobilenet.load()
      this.webcamPredictions()
    },
    webcamPredictions () {
      if (!this.model) return window.requestAnimationFrame(this.webcamPredictions);
      // console.log('masuk')
      this.model.classify(this.video).then((predictions) => {
        this.result = predictions[0].className
      })
      setTimeout(function(){}, 1000);
      window.requestAnimationFrame(this.webcamPredictions)
    }
  },
  created () {
    this.startVideo()
    this.loadModel()
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}

video {
  max-height: 500px;
  transform: rotateY(180deg);
}
</style>
