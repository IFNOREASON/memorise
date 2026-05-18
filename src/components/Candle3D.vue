<template>
  <div ref="containerRef" class="candle-3d-container"></div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch } from 'vue'
import * as THREE from 'three'

interface Props {
  position?: number[]
  scale?: number
}

const props = withDefaults(defineProps<Props>(), {
  position: () => [0, -1.5, 0.8],
  scale: 1
})

const containerRef = ref<HTMLDivElement | null>(null)

let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let candleGroup: THREE.Group | null = null
let animationId: number | null = null
let flameLight: THREE.PointLight | null = null

const createCandle = () => {
  candleGroup = new THREE.Group()
  
  const candleHeight = 1.2
  const candleRadius = 0.15
  
  const candleGeometry = new THREE.CylinderGeometry(candleRadius, candleRadius * 1.1, candleHeight, 32)
  const candleMaterial = new THREE.MeshStandardMaterial({
    color: 0xfff5e6,
    roughness: 0.8,
    metalness: 0.1,
    emissive: 0xffcc66,
    emissiveIntensity: 0.1
  })
  const candle = new THREE.Mesh(candleGeometry, candleMaterial)
  candle.position.y = candleHeight / 2
  candle.castShadow = true
  candleGroup.add(candle)
  
  const wickGeometry = new THREE.CylinderGeometry(0.02, 0.02, 0.15, 8)
  const wickMaterial = new THREE.MeshStandardMaterial({
    color: 0x333333,
    roughness: 0.9
  })
  const wick = new THREE.Mesh(wickGeometry, wickMaterial)
  wick.position.y = candleHeight + 0.07
  candleGroup.add(wick)
  
  const flameHeight = 0.4
  const flameGeometry = new THREE.ConeGeometry(0.1, flameHeight, 16, 1, true)
  const flameMaterial = new THREE.ShaderMaterial({
    uniforms: {
      time: { value: 0 },
      color: { value: new THREE.Color(0xff6600) }
    },
    vertexShader: `
      varying vec2 vUv;
      varying float vHeight;
      uniform float time;
      
      void main() {
        vUv = uv;
        vHeight = position.y;
        
        vec3 pos = position;
        
        float wave = sin(time * 3.0 + position.y * 5.0) * 0.02 * position.y;
        pos.x += wave;
        pos.z += wave * 0.5;
        
        float flicker = sin(time * 8.0) * 0.01;
        pos.x += flicker;
        pos.z += flicker;
        
        gl_Position = projectionMatrix * modelViewMatrix * vec4(pos, 1.0);
      }
    `,
    fragmentShader: `
      varying vec2 vUv;
      varying float vHeight;
      uniform vec3 color;
      uniform float time;
      
      void main() {
        float intensity = vHeight * 2.0;
        float alpha = smoothstep(0.0, 0.5, vHeight) * (1.0 - smoothstep(0.5, 1.0, vHeight)) * 2.0;
        
        vec3 flameColor = mix(vec3(1.0, 0.9, 0.3), vec3(1.0, 0.3, 0.0), vHeight);
        
        float flicker = sin(time * 10.0) * 0.1 + 0.9;
        flameColor *= flicker;
        
        gl_FragColor = vec4(flameColor, alpha * 0.9);
      }
    `,
    transparent: true,
    blending: THREE.AdditiveBlending,
    side: THREE.DoubleSide
  })
  
  const flame = new THREE.Mesh(flameGeometry, flameMaterial)
  flame.position.y = candleHeight + 0.15 + flameHeight / 2
  candleGroup.add(flame)
  
  const glowGeometry = new THREE.SphereGeometry(0.3, 16, 16)
  const glowMaterial = new THREE.MeshBasicMaterial({
    color: 0xffaa33,
    transparent: true,
    opacity: 0.2,
    blending: THREE.AdditiveBlending
  })
  const glow = new THREE.Mesh(glowGeometry, glowMaterial)
  glow.position.y = candleHeight + 0.3
  candleGroup.add(glow)
  
  const baseGeometry = new THREE.CylinderGeometry(0.2, 0.25, 0.1, 32)
  const baseMaterial = new THREE.MeshStandardMaterial({
    color: 0x8B4513,
    roughness: 0.7,
    metalness: 0.3
  })
  const base = new THREE.Mesh(baseGeometry, baseMaterial)
  base.position.y = -0.05
  base.castShadow = true
  candleGroup.add(base)
  
  candleGroup.position.set(0, 0, 0)
  candleGroup.scale.setScalar(props.scale)
  
  return { candleGroup, flameMaterial, glow }
}

const initScene = () => {
  if (!containerRef.value) return
  
  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight
  
  scene = new THREE.Scene()
  
  camera = new THREE.PerspectiveCamera(45, width / height, 0.1, 1000)
  camera.position.set(0, 0.5, 2.5)
  
  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: true
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFSoftShadowMap
  
  containerRef.value.appendChild(renderer.domElement)
  
  const ambientLight = new THREE.AmbientLight(0xffffff, 0.3)
  scene.add(ambientLight)
  
  const { candleGroup: candle, flameMaterial, glow } = createCandle()
  candleGroup = candle
  scene.add(candleGroup)
  
  flameLight = new THREE.PointLight(0xff6600, 1, 5)
  flameLight.position.set(0, 0.3, 0)
  flameLight.castShadow = true
  scene.add(flameLight)
  
  const animate = (time: number) => {
    animationId = requestAnimationFrame(animate)
    
    if (flameMaterial) {
      flameMaterial.uniforms.time.value = time * 0.001
    }
    
    if (flameLight) {
      const flicker = Math.sin(time * 0.01) * 0.2 + 0.8
      flameLight.intensity = flicker
      flameLight.position.x = Math.sin(time * 0.005) * 0.02
      flameLight.position.z = Math.cos(time * 0.005) * 0.02
    }
    
    if (candleGroup) {
      candleGroup.rotation.y += 0.002
    }
    
    if (renderer && scene && camera) {
      renderer.render(scene, camera)
    }
  }
  
  animate(0)
}

const handleResize = () => {
  if (!containerRef.value || !camera || !renderer) return
  
  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight
  
  camera.aspect = width / height
  camera.updateProjectionMatrix()
  renderer.setSize(width, height)
}

onMounted(() => {
  initScene()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  
  if (animationId) {
    cancelAnimationFrame(animationId)
  }
  
  if (renderer) {
    renderer.dispose()
    if (renderer.domElement.parentNode) {
      renderer.domElement.parentNode.removeChild(renderer.domElement)
    }
  }
  
  if (candleGroup) {
    candleGroup.traverse((child) => {
      const mesh = child as THREE.Mesh
      if (mesh.isMesh) {
        if (mesh.geometry) {
          mesh.geometry.dispose()
        }
        if (mesh.material) {
          if (Array.isArray(mesh.material)) {
            mesh.material.forEach(mat => mat.dispose())
          } else {
            mesh.material.dispose()
          }
        }
      }
    })
  }
})
</script>

<style scoped>
.candle-3d-container {
  position: absolute;
  bottom: 60px;
  right: 20px;
  width: 200px;
  height: 200px;
  pointer-events: none;
  z-index: 10;
}
</style>
