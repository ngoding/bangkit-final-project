<template>
  <div class="bangkit">
    <h1>Hello world!</h1>

    <div v-if="this.initialise">
      <h3 v-if="this.loadingModel">Loading model</h3>
      <h3 v-if="!this.loadingModel && this.initialise" >Initializing</h3>
      <pulse-loader size="10px"/>
    </div>

    <button @click="changeCamera()">Change camera</button>
    <div id="liveView" class="webcam">
      <p id="webcamPredictions">{{this.result}}</p>
      <video v-bind:class="{ mirror: this.frontCamera }" id="video" autoplay muted playsinline/>
    </div>

  </div>
</template>

<script>
import Vue from 'vue'
import AsyncComputed from 'vue-async-computed'
import PulseLoader from 'vue-spinner/src/PulseLoader.vue'
const nj = require('../../public/numjs')

// import * as tf from '@tensorflow/tfjs';
import * as faceApi from 'face-api.js'

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
    liveView () {
      return document.getElementById('liveView')
    },
    context() {
      if (this.canvas) return this.canvas.getContext('2d')
      return null
    },
  },
  data () {
    return {
      loadingModel: true,
      videoReady: false,
      frontCamera: true,
      displaySize: null,
      initialise: true,
      canvas: null,
      result: null,
      test:null
    }
  },
  methods: {
    changeCamera () {
      this.clearCanvas()
      this.frontCamera = !this.frontCamera
      this.frontCamera 
      // mirror video and canvas if using front camera
      ? this.canvas.style.transform = 'rotateY(180deg)'
      : this.canvas.style.transform = 'initial'
      this.startVideo()
    },
    checkVideoReady() {
      if (this.video.readyState < 3) return setTimeout(window.requestAnimationFrame(this.checkVideoReady), 1000);
      this.videoReady = true
    },
    async startVideo () {
      this.videoReady = false
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {facingMode: this.frontCamera ? 'user' : 'environment'}
      })
      this.video.srcObject = stream
      this.checkVideoReady()
    },
    async loadModel () {
      // use mtcnn
      await faceApi.nets.mtcnn.loadFromUri('/models')

      // use tiny face
      // await faceApi.nets.tinyFaceDetector.loadFromUri('/models')

      this.loadingModel = false
      this.webcamPredictions()
    },
    async webcamPredictions() {
      // check if camera is ready and face is detected
      if (!this.videoReady) return setTimeout(window.requestAnimationFrame(this.webcamPredictions), 1000)

      // use mtcnn
      let result = await faceApi.detectSingleFace(this.video, new faceApi.MtcnnOptions({minFaceSize: 160}))
      if (result && this.initialise) {
        console.log(result)
        this.test = nj.array([1,2,3])
        this.initialise = false
      }

      // use tiny face
      // let result = await faceApi.detectSingleFace(this.video, new faceApi.TinyFaceDetectorOptions())

      if (!result) {
        this.clearCanvas()
        return window.requestAnimationFrame(this.webcamPredictions)
      }

      // draw the tracking box, repeat.
      this.clearCanvas()
      faceApi.draw.drawDetections(this.canvas, result)
      setTimeout(window.requestAnimationFrame(this.webcamPredictions), 200)
    },
    createCanvas() {
      if (!this.videoReady) return setTimeout(window.requestAnimationFrame(this.createCanvas), 1000);
      this.canvas = faceApi.createCanvasFromMedia(this.video)

      // add style
      this.canvas.style.position = 'absolute'
      if (this.frontCamera) {
        this.canvas.style.transform = 'rotateY(180deg)'
      }

      // append canvas element
      this.liveView.append(this.canvas)

      // get webcam video size
      const actualVideoSize = this.video.getBoundingClientRect()
      this.displaySize = {width: actualVideoSize['width'], height: actualVideoSize['height']}

      // change faceApi dimension
      faceApi.matchDimensions(this.canvas, this.displaySize)
    },
    clearCanvas() {
      if (this.canvas) {
        this.canvas.getContext('2d').clearRect(0, 0, this.canvas.width, this.canvas.height)
      }
    }
  },
  created () {
    this.loadModel()
    this.startVideo()
    this.createCanvas()
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
}

canvas {
  position: absolute;
}

.mirror {
  transform: rotateY(180deg);
}

#liveView {
  display: flex;
  justify-content: center;
  align-items: center;
}

button {
  padding: 5px;
  background-color: white;
  margin-bottom: 1em;
  border: 2px darkgrey solid;
}
</style>
