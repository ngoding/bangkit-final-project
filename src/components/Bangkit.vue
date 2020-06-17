<template>
  <div class="bangkit">
    <h1>Hello world!</h1>
    <h3 v-if="!this.model">
      Loading model
    </h3>
    <pulse-loader v-if="!this.model" size="10px"/>
    <button @click="changeCamera()">Toggle camera</button>
    <div id="liveView" class="webcam">
      <video v-bind:class="{ mirror: this.frontCamera }" id="video" width="100%" height="100%" autoplay muted playsinline/>
      <p id="webcamPredictions">{{this.result}}</p>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'
import AsyncComputed from 'vue-async-computed'
import PulseLoader from 'vue-spinner/src/PulseLoader.vue'

// import * as tf from '@tensorflow/tfjs';
// import * as mobilenet from '@tensorflow-models/mobilenet';
import * as cocoSsd from '@tensorflow-models/coco-ssd'

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
    }
  },
  data () {
    return {
      model: null,
      loadingModel: false,
      result: null,
      frontCamera: true,
      children: []
    }
  },
  methods: {
    changeCamera () {
      this.frontCamera = !this.frontCamera
      this.startVideo()
    },
    async startVideo () {
      const stream = await navigator.mediaDevices.getUserMedia({
        audio: false,
        video: {facingMode: this.frontCamera ? 'user' : 'environment'}
      })
      this.video.srcObject = stream
    },
    async loadModel () {
      // const mobilenet = require('@tensorflow-models/mobilenet');
      // this.model = await tf.loadGraphModel('/model.json')
      // this.model = await mobilenet.load()
      // this.webcamPredictionsMobileNet()

      this.model = await cocoSsd.load()
      this.webcamPredictionsCoco()
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
      if (!this.model) return window.requestAnimationFrame(this.webcamPredictionsMobileNet);
      if (this.video.readyState < 3) return window.requestAnimationFrame(this.webcamPredictionsMobileNet);
      let self = this
      this.model.detect(this.video).then(function (predictions) {
        // Remove any highlighting we did previous frame.
        for (let i = 0; i < self.children.length; i++) {
          self.liveView.removeChild(self.children[i]);
        }
        self.children.splice(0);
        
        // Now lets loop through predictions and draw them to the live view if
        // they have a high confidence score.
        for (let n = 0; n < predictions.length; n++) {
          // If we are over 66% sure we are sure we classified it right, draw it!
          if (predictions[n].score > 0.66) {
            self.result = `${predictions[n].class} with ${Math.round(parseFloat(predictions[n].score) * 100)} % confidence.`;
            // const p = document.createElement('p');
            // p.innerText = predictions[n].class  + ' - with ' 
            //     + Math.round(parseFloat(predictions[n].score) * 100) 
            //     + '% confidence.';
            // p.style = 'margin-left: ' + predictions[n].bbox[0] + 'px; margin-top: '
            //     + (predictions[n].bbox[1] - 10) + 'px; width: ' 
            //     + (predictions[n].bbox[2] - 10) + 'px; top: 0; left: 0;';

            // const highlighter = document.createElement('div');
            // highlighter.setAttribute('class', 'highlighter');
            // highlighter.style = 'left: ' + predictions[n].bbox[0] + 'px; top: '
            //     + predictions[n].bbox[1] + 'px; width: ' 
            //     + predictions[n].bbox[2] + 'px; height: '
            //     + predictions[n].bbox[3] + 'px;';

            // self.liveView.appendChild(highlighter);
            // self.liveView.appendChild(p);
            // self.children.push(highlighter);
            // self.children.push(p);
          }
        }
        
        // Call this function again to keep predicting when the browser is ready.
        window.requestAnimationFrame(self.webcamPredictionsCoco);
      });
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

.mirror {
  transform: rotateY(180deg);
}

button {
  padding: 5px;
  background-color: white;
  margin-bottom: 1em;
  border: 2px darkgrey solid;
}
/* 
.highlighter {
  background: rgba(0, 255, 0, 0.25);
  border: 1px dashed #fff;
  z-index: 1;
  position: absolute;
}
.webcam p {
  position: absolute;
  padding: 5px;
  background-color: rgba(255, 111, 0, 0.85);
  color: #FFF;
  border: 1px dashed rgba(255, 255, 255, 0.7);
  z-index: 2;
  font-size: 12px;
}

.webcam {
  position: relative;
  float: left;
  width: 48%;
  margin: 2% 1%;
  cursor: pointer;
} */
</style>
