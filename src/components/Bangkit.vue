<template>
  <div class="bangkit">
    <h1>Hello world!</h1>
    <h3 v-if="this.loadingModel">
      Loading model
    </h3>
    <pulse-loader v-if="this.loadingModel" size="10px"/>
    <button @click="changeCamera()">Toggle camera</button>
    <div id="liveView" class="webcam">
      <p id="webcamPredictions">{{this.result}}</p>
      <video v-bind:class="{ mirror: this.frontCamera }" id="video" autoplay muted playsinline/>
      <!-- <canvas id="overlay" v-bind:class="{ mirror: this.frontCamera }"></canvas> -->
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import AsyncComputed from 'vue-async-computed'
import PulseLoader from 'vue-spinner/src/PulseLoader.vue'

// import * as tf from '@tensorflow/tfjs';
// import * as mobilenet from '@tensorflow-models/mobilenet';
// import * as cocoSsd from '@tensorflow-models/coco-ssd'
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
    }
  },
  data () {
    return {
      model: null,
      loadingModel: true,
      result: null,
      frontCamera: true,
      children: [],
      canvas: null,
      displaySize: null,
    }
  },
  methods: {
    changeCamera () {
      this.frontCamera = !this.frontCamera
      this.frontCamera 
      ? this.canvas.style.transform = 'rotateY(180deg)'
      : this.canvas.style.transform = 'initial'
      this.startVideo()
    },
    async startVideo () {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {facingMode: this.frontCamera ? 'user' : 'environment'}
      })
      this.video.srcObject = stream
      this.createCanvas()
    },
    async loadModel () {
      // this.model = await mobilenet.load()
      // this.model = await cocoSsd.load()
      // await faceApi.nets.mtcnn.loadFromUri('/models')
      await faceApi.nets.tinyFaceDetector.loadFromUri('/models')
      this.loadingModel = false

      // this.webcamPredictionsCoco()
      // this.webcamPredictionsMobileNet()
      this.webcamPredictionsMTCNN()

    },
    webcamPredictionsMobileNet () {
      if (!this.model) return window.requestAnimationFrame(this.webcamPredictionsMobileNet);
      if (this.video.readyState < 3) return window.requestAnimationFrame(this.webcamPredictionsMobileNet);

      this.model.classify(this.video).then((predictions) => {
        this.result = predictions[0].className
      })

      setTimeout(function(){}, 1000);
      window.requestAnimationFrame(this.webcamPredictionsMobileNet)
    },
    webcamPredictionsCoco() {
      if (!this.model) return window.requestAnimationFrame(this.webcamPredictionsCoco);
      if (this.video.readyState < 3) return window.requestAnimationFrame(this.webcamPredictionsCoco);

      let self = this
      this.model.detect(this.video).then(function (predictions) {
        for (let n = 0; n < predictions.length; n++) {
          // If we are over 66% sure we are sure we classified it right, draw it!
          if (predictions[n].score > 0.66) {
            self.result = `${predictions[n].class} with ${Math.round(parseFloat(predictions[n].score) * 100)} % confidence.`;
            // self.drawBox(predictions[n].bbox)
          }
        }
        // Call this function again to keep predicting when the browser is ready.
        window.requestAnimationFrame(self.webcamPredictionsCoco);
      });
    },
    async webcamPredictionsMTCNN() {
      // check if camera is ready
      if (this.video.readyState < 3) return setTimeout(window.requestAnimationFrame(this.webcamPredictionsMTCNN), 1000)

      // check if face is found and resize the detection
      let result = await faceApi.detectSingleFace(this.video, new faceApi.TinyFaceDetectorOptions())
      if (!result) return setTimeout(window.requestAnimationFrame(this.webcamPredictionsMTCNN), 1000)
      const resizedDetection = faceApi.resizeResults(result, this.displaySize)

      // draw the tracking box, repeat.
      this.clearCanvas()
      faceApi.draw.drawDetections(this.canvas, resizedDetection)
      setTimeout(window.requestAnimationFrame(this.webcamPredictionsMTCNN), 1000)
    },
    createCanvas() {
      // wait for the webcam to actually be ready
      if (this.video.readyState < 3) return setTimeout(window.requestAnimationFrame(this.createCanvas), 1000);
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
      this.canvas.getContext('2d').clearRect(0, 0, this.canvas.width, this.canvas.height)
    }
  },
  created () {
    this.loadModel()
    this.startVideo()
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
