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
      <video v-bind:class="{ mirror: this.frontCamera }" id="video" autoplay muted playsinline/>
    </div>

    <!-- <p>{{this.result}}</p> -->
    <div v-if="this.topTen">
      <p>Top ten match:</p>
      <ul>
        <li v-for="match in this.topTen" :key="match[0]">
          {{`${match[0]} (${match[1].toFixed(3)}%)`}}
        </li>
      </ul>

    </div>

  </div>
</template>

<script>
import Vue from 'vue'
import axios from 'axios'
import AsyncComputed from 'vue-async-computed'
import PulseLoader from 'vue-spinner/src/PulseLoader.vue'

import * as faceApi from 'face-api.js'

// in-browser prediction failed. Solution: backend prediction.
// const nj = require('../../public/numjs')
// import * as tf from '@tensorflow/tfjs'
// import classes from '../../public/label_classes.json'

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
      imageCapture: null,
      faceNetModel: null,
      vectorClassifierModel: null,
      // labelClasses: classes,
      canvas: null,
      result: null,
      topTen: null
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
      this.imageCapture = new ImageCapture(stream.getVideoTracks()[0])
      this.checkVideoReady()
    },
    async loadModel () {
      // use mtcnn
      await faceApi.nets.mtcnn.loadFromUri('/models')

      // lambda layers not supported in js. Solution: get embeddings from backend
      // this.faceNetModel = await tf.loadLayersModel('/models/facenet/model.json');

      // tensor number mismatch. Solution: full prediction from backend.
      // this.vectorClassifierModel = await tf.loadLayersModel('/models/vector_classifier/model.json');

      this.loadingModel = false
      this.webcamPredictions()
    },
    async webcamPredictions() {
      // check if camera is ready and face is detected
      if (!this.videoReady) return setTimeout(window.requestAnimationFrame(this.webcamPredictions), 1000)

      // use mtcnn
      let result = await faceApi.detectSingleFace(this.video, new faceApi.MtcnnOptions({minFaceSize: 160}))

      if (result && this.initialise) {
        this.namePredictions()
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
    async namePredictions(){
      if (!this.videoReady) return setTimeout(window.requestAnimationFrame(this.namePredictions), 1000)
      let data = new FormData()
      data.append('name', 'image')
      let config = {
        header : {
          'Content-Type' : 'multipart/form-data'
        }
      }

      await this.imageCapture.takePhoto().then((blob) => {
        data.append('image', blob)
      })

      await axios.post(`http://localhost:3000/predict`,data, config)
        .then(response => {
          // this.result = `${response.data.name} with ${response.data.probability.toFixed(3)} % probability`
          this.topTen = response.data.top10
        })
        .catch(e => {
          console.log(e)
        })

      // tensor error, could not proceed.
      // await axios.post(`http://localhost:3000/get-embeddings`,data, config)
      //   .then(response => {
      //     console.log(response)
      //     const embedding = nj.array(response.data.embedding)
      //     console.log(embedding)
      //     // const predictedClass = this.vectorClassifierModel.predict_classes(embedding)
      //     const probability = this.vectorClassifierModel.predict(embedding)
      //     console.log(probability)
      //     // predicted_name = face_classes[predicted_class[0]]
      //   })
      //   .catch(e => {
      //     console.log(e)
      //   })
      setTimeout(window.requestAnimationFrame(this.namePredictions), 2000)
    },
    // predictName() {

    // },
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
  display: block;
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
