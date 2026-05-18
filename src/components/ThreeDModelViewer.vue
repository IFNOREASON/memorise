<template>
  <div ref="containerRef" class="three-d-viewer" :class="{ 'full-height': fullHeight }">
    <div v-if="loading" class="loading-overlay">
      <div class="loading-spinner"></div>
      <p class="text-sm text-gray-500 mt-2">加载3D模型中...</p>
    </div>
    <div v-if="error" class="error-overlay">
      <Icon icon="solar:danger-triangle-bold" class="text-4xl text-amber-500 mb-2" />
      <p class="text-sm text-gray-600">{{ error }}</p>
    </div>
    
    <div v-if="debugMode" class="absolute top-2 right-2 z-20 bg-black/70 text-white text-xs p-3 rounded-lg max-w-xs max-h-64 overflow-y-auto">
      <h4 class="font-bold mb-1">调试信息</h4>
      <div v-if="debugInfo" class="space-y-1">
        <p>模型: {{ debugInfo.modelName }}</p>
        <p>材质数: {{ debugInfo.materialCount }}</p>
        <p>网格数: {{ debugInfo.meshCount }}</p>
        <p>有纹理: {{ debugInfo.hasTextures ? '是' : '否' }}</p>
        <p v-if="debugInfo.materialTypes">材质类型: {{ debugInfo.materialTypes.join(', ') }}</p>
      </div>
      <button @click="toggleDebugMode" class="mt-2 px-2 py-1 bg-red-500 rounded text-xs">关闭调试</button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, computed } from 'vue'
import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js'
import { DRACOLoader } from 'three/examples/jsm/loaders/DRACOLoader.js'
import { MeshoptDecoder } from 'three/examples/jsm/libs/meshopt_decoder.module.js'
import { Icon } from '@iconify/vue'

interface Props {
  modelUrl?: string
  backgroundColor?: number
  ambientLightIntensity?: number
  autoRotate?: boolean
  fullHeight?: boolean
  wireframe?: boolean
  debugMode?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  modelUrl: undefined,
  backgroundColor: 0xFAF7F2,
  ambientLightIntensity: 0.6,
  autoRotate: true,
  fullHeight: false,
  wireframe: false,
  debugMode: false
})

interface Emits {
  (e: 'loaded'): void
  (e: 'error', error: string): void
}

const emit = defineEmits<Emits>()

const containerRef = ref<HTMLDivElement | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const showDebug = ref(false)
const debugInfo = ref<{
  modelName: string
  materialCount: number
  meshCount: number
  hasTextures: boolean
  materialTypes: string[]
} | null>(null)

let scene: THREE.Scene | null = null
let camera: THREE.PerspectiveCamera | null = null
let renderer: THREE.WebGLRenderer | null = null
let controls: OrbitControls | null = null
let animationId: number | null = null
let model: THREE.Object3D | null = null

const backgroundColor = computed(() => new THREE.Color(props.backgroundColor))

const toggleDebugMode = () => {
  showDebug.value = !showDebug.value
}

const initScene = () => {
  if (!containerRef.value) return

  scene = new THREE.Scene()
  scene.background = backgroundColor.value

  const width = containerRef.value.clientWidth
  const height = containerRef.value.clientHeight

  camera = new THREE.PerspectiveCamera(
    45,
    width / height,
    0.1,
    1000
  )
  camera.position.set(0, 1.5, 4)

  renderer = new THREE.WebGLRenderer({
    antialias: true,
    alpha: true,
    preserveDrawingBuffer: true
  })
  renderer.setSize(width, height)
  renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
  renderer.shadowMap.enabled = true
  renderer.shadowMap.type = THREE.PCFShadowMap
  
  renderer.outputColorSpace = THREE.SRGBColorSpace
  
  renderer.toneMapping = THREE.ACESFilmicToneMapping
  renderer.toneMappingExposure = 1.2
  
  renderer.useLegacyLights = false

  containerRef.value.appendChild(renderer.domElement)

  const createGradientEnvMap = () => {
    const size = 256
    const canvas = document.createElement('canvas')
    canvas.width = size
    canvas.height = size
    const ctx = canvas.getContext('2d')!
    
    const gradient = ctx.createLinearGradient(0, 0, 0, size)
    gradient.addColorStop(0, '#e8f4ff')
    gradient.addColorStop(0.3, '#b8d4f0')
    gradient.addColorStop(0.7, '#8bb8cc')
    gradient.addColorStop(1, '#6a8b9a')
    ctx.fillStyle = gradient
    ctx.fillRect(0, 0, size, size)
    
    const texture = new THREE.CanvasTexture(canvas)
    texture.mapping = THREE.EquirectangularReflectionMapping
    texture.colorSpace = THREE.SRGBColorSpace
    
    const pmremGenerator = new THREE.PMREMGenerator(renderer!)
    const envMapRT = pmremGenerator.fromEquirectangular(texture)
    texture.dispose()
    pmremGenerator.dispose()
    
    return envMapRT.texture
  }

  const envMap = createGradientEnvMap()
  scene.environment = envMap

  controls = new OrbitControls(camera, renderer.domElement)
  controls.enableDamping = true
  controls.dampingFactor = 0.05
  controls.minDistance = 1
  controls.maxDistance = 15
  controls.maxPolarAngle = Math.PI / 2 + 0.5
  controls.autoRotate = props.autoRotate
  controls.autoRotateSpeed = 1.0
  controls.enablePan = false
  controls.target.set(0, 1, 0)
  controls.update()

  const hemiLight = new THREE.HemisphereLight(0xffffff, 0x888888, 0.8)
  hemiLight.position.set(0, 20, 0)
  scene.add(hemiLight)

  const mainLight = new THREE.DirectionalLight(0xffffff, 2.0)
  mainLight.position.set(3, 5, 3)
  mainLight.castShadow = true
  mainLight.shadow.mapSize.width = 2048
  mainLight.shadow.mapSize.height = 2048
  mainLight.shadow.camera.near = 0.5
  mainLight.shadow.camera.far = 50
  mainLight.shadow.camera.left = -10
  mainLight.shadow.camera.right = 10
  mainLight.shadow.camera.top = 10
  mainLight.shadow.camera.bottom = -10
  scene.add(mainLight)

  const mainLight2 = new THREE.DirectionalLight(0xffffff, 1.2)
  mainLight2.position.set(-3, 4, -3)
  scene.add(mainLight2)

  const fillLight = new THREE.DirectionalLight(0xffffff, 0.8)
  fillLight.position.set(-5, 3, 5)
  scene.add(fillLight)

  const rimLight = new THREE.DirectionalLight(0xffffff, 0.6)
  rimLight.position.set(0, 5, -5)
  scene.add(rimLight)

  const bottomLight = new THREE.DirectionalLight(0xffffff, 0.3)
  bottomLight.position.set(0, -1, 0)
  scene.add(bottomLight)

  const ambientLight = new THREE.AmbientLight(0xffffff, 0.5)
  scene.add(ambientLight)

  const floorGeometry = new THREE.CircleGeometry(4, 64)
  const floorMaterial = new THREE.MeshStandardMaterial({
    color: 0xE8D5C4,
    roughness: 0.9,
    metalness: 0.0
  })
  const floor = new THREE.Mesh(floorGeometry, floorMaterial)
  floor.rotation.x = -Math.PI / 2
  floor.position.y = -0.01
  floor.receiveShadow = true
  scene.add(floor)

  if (props.modelUrl) {
    loadModel(props.modelUrl)
  } else {
    createPlaceholderHuman()
  }

  animate()
}

const createPlaceholderHuman = () => {
  if (!scene) return

  const humanGroup = new THREE.Group()

  const bodyGeometry = new THREE.CapsuleGeometry(0.25, 0.7, 8, 16)
  const bodyMaterial = new THREE.MeshStandardMaterial({
    color: props.wireframe ? 0x8B6F4E : 0x4A4A4A,
    roughness: 0.6,
    metalness: 0.1,
    wireframe: props.wireframe
  })
  const body = new THREE.Mesh(bodyGeometry, bodyMaterial)
  body.position.y = 0.9
  body.castShadow = true
  humanGroup.add(body)

  const headGeometry = new THREE.SphereGeometry(0.2, 16, 16)
  const headMaterial = new THREE.MeshStandardMaterial({
    color: props.wireframe ? 0x6B5342 : 0xFFE0BD,
    roughness: 0.8,
    metalness: 0,
    wireframe: props.wireframe
  })
  const head = new THREE.Mesh(headGeometry, headMaterial)
  head.position.y = 1.65
  head.castShadow = true
  humanGroup.add(head)

  const leftArmGeometry = new THREE.CapsuleGeometry(0.07, 0.4, 8, 8)
  const leftArmMaterial = new THREE.MeshStandardMaterial({
    color: props.wireframe ? 0x6B5342 : 0x4A4A4A,
    roughness: 0.6,
    wireframe: props.wireframe
  })
  const leftArm = new THREE.Mesh(leftArmGeometry, leftArmMaterial)
  leftArm.position.set(-0.35, 1.1, 0)
  leftArm.rotation.z = Math.PI / 6
  leftArm.castShadow = true
  humanGroup.add(leftArm)

  const rightArm = new THREE.Mesh(leftArmGeometry, leftArmMaterial)
  rightArm.position.set(0.35, 1.1, 0)
  rightArm.rotation.z = -Math.PI / 6
  rightArm.castShadow = true
  humanGroup.add(rightArm)

  const leftLegGeometry = new THREE.CapsuleGeometry(0.08, 0.45, 8, 8)
  const leftLegMaterial = new THREE.MeshStandardMaterial({
    color: props.wireframe ? 0x6B5342 : 0x3A3A3A,
    roughness: 0.7,
    wireframe: props.wireframe
  })
  const leftLeg = new THREE.Mesh(leftLegGeometry, leftLegMaterial)
  leftLeg.position.set(-0.12, 0.15, 0)
  leftLeg.castShadow = true
  humanGroup.add(leftLeg)

  const rightLeg = new THREE.Mesh(leftLegGeometry, leftLegMaterial)
  rightLeg.position.set(0.12, 0.15, 0)
  rightLeg.castShadow = true
  humanGroup.add(rightLeg)

  model = humanGroup
  scene!.add(humanGroup)
  
  loading.value = false
  emit('loaded')
}

const processMaterial = (material: THREE.Material) => {
  console.log('处理材质:', material.type, material.name)
  
  if (props.wireframe) {
    ;(material as any).wireframe = true
    return
  }

  const matAny = material as any
  
  if (matAny.map) {
    matAny.map.colorSpace = THREE.SRGBColorSpace
    matAny.map.needsUpdate = true
  }
  
  if (matAny.roughnessMap) {
    matAny.roughnessMap.colorSpace = THREE.NoColorSpace
  }
  
  if (matAny.normalMap) {
    matAny.normalMap.colorSpace = THREE.NoColorSpace
  }
  
  if (matAny.metalnessMap) {
    matAny.metalnessMap.colorSpace = THREE.NoColorSpace
  }
  
  if (matAny.emissiveMap) {
    matAny.emissiveMap.colorSpace = THREE.SRGBColorSpace
  }
  
  if (matAny.aoMap) {
    matAny.aoMap.colorSpace = THREE.NoColorSpace
  }
  
  if (matAny.displacementMap) {
    matAny.displacementMap.colorSpace = THREE.NoColorSpace
  }
  
  if (matAny.lightMap) {
    matAny.lightMap.colorSpace = THREE.NoColorSpace
  }
  
  if (matAny.bumpMap) {
    matAny.bumpMap.colorSpace = THREE.NoColorSpace
  }
  
  if (matAny.envMap) {
    matAny.envMap.colorSpace = THREE.SRGBColorSpace
  }
  
  if (matAny.alphaMap) {
    matAny.alphaMap.colorSpace = THREE.NoColorSpace
  }
  
  if (matAny.aoMapIntensity !== undefined) {
    matAny.aoMapIntensity = 1.0
  }
  
  if (matAny.normalScale) {
    matAny.normalScale.set(1, 1)
  }
  
  if (material instanceof THREE.MeshStandardMaterial || 
      material instanceof THREE.MeshPhysicalMaterial) {
    console.log('  - 是 PBR 材质')
    
    if (!material.map) {
      material.color.convertSRGBToLinear()
    }
    
    if (material.emissive) {
      material.emissive.convertSRGBToLinear()
    }
    
    if (!material.roughnessMap && material.roughness > 0.8) {
      material.roughness = 0.5
    }
    
    if (!material.metalnessMap && material.metalness > 0.8) {
      material.metalness = 0.1
    }
    
    material.needsUpdate = true
    console.log('  - 材质颜色:', material.color ? '#' + material.color.getHexString() : '无')
    console.log('  - 金属度:', material.metalness)
    console.log('  - 粗糙度:', material.roughness)
    
    if ((material as any).vertexColors) {
      console.log('  - 材质有vertexColors')
      if (!material.map && !material.roughnessMap && !material.normalMap && !material.metalnessMap) {
        material.color.setHex(0xffffff)
      }
    }
  } else if (material instanceof THREE.MeshBasicMaterial) {
    console.log('  - 是基础材质')
    if (!material.map) {
      material.color.convertSRGBToLinear()
    }
    material.needsUpdate = true
  } else if (material instanceof THREE.MeshLambertMaterial) {
    console.log('  - 是 Lambert 材质')
    if (!material.map) {
      material.color.convertSRGBToLinear()
    }
    if (material.emissive) {
      material.emissive.convertSRGBToLinear()
    }
    material.needsUpdate = true
  } else if (material instanceof THREE.MeshPhongMaterial) {
    console.log('  - 是 Phong 材质')
    if (!material.map) {
      material.color.convertSRGBToLinear()
    }
    if (material.emissive) {
      material.emissive.convertSRGBToLinear()
    }
    if (material.specular) {
      material.specular.convertSRGBToLinear()
    }
    material.needsUpdate = true
  } else if (material instanceof THREE.MeshMatcapMaterial) {
    console.log('  - 是 Matcap 材质')
    if (material.matcap) {
      material.matcap.colorSpace = THREE.SRGBColorSpace
    }
    material.needsUpdate = true
  } else if (material instanceof THREE.MeshDepthMaterial) {
    console.log('  - 是深度材质')
    material.needsUpdate = true
  } else if (material instanceof THREE.MeshNormalMaterial) {
    console.log('  - 是法向材质')
    material.needsUpdate = true
  } else {
    console.warn('  - 未知材质类型，已应用通用处理')
    material.needsUpdate = true
  }
}

const loadModel = (url: string) => {
  if (!scene) return

  console.log('开始加载模型:', url)
  loading.value = true

  const loader = new GLTFLoader()
  
  const dracoLoader = new DRACOLoader()
  dracoLoader.setDecoderPath('https://www.gstatic.com/draco/versioned/decoders/1.5.6/')
  loader.setDRACOLoader(dracoLoader)
  
  loader.setMeshoptDecoder(MeshoptDecoder)

  loader.load(
    url,
    (gltf) => {
      console.log('模型加载成功!')
      console.log('GLTF数据:', gltf)
      
      if (model) {
        scene!.remove(model)
      }

      model = gltf.scene
      
      const materialTypes = new Set<string>()
      let hasTextures = false
      let meshCount = 0
      let materialCount = 0
      
      console.log('=== 开始遍历模型 ===')
      
      model.traverse((child) => {
        const mesh = child as THREE.Mesh
        
        if (mesh.isMesh || (child as any).isSkinnedMesh) {
          meshCount++
          console.log(`\n发现网格 [${meshCount}]:`, mesh.name || '未命名', (child as any).isSkinnedMesh ? '(蒙皮网格)' : '')
          
          mesh.castShadow = true
          mesh.receiveShadow = true
          
          mesh.frustumCulled = false
          
          const hasVertexColors = mesh.geometry && mesh.geometry.attributes.color
          
          if (mesh.geometry) {
            console.log('  几何体属性:', Object.keys(mesh.geometry.attributes))
            if (hasVertexColors) {
              console.log('  检测到顶点颜色属性')
            }
            
            mesh.geometry.computeBoundingBox()
            mesh.geometry.computeBoundingSphere()
          }
          
          if (mesh.material) {
            const materials = Array.isArray(mesh.material) ? mesh.material : [mesh.material]
            
            materials.forEach((mat, idx) => {
              materialCount++
              materialTypes.add(mat.type)
              console.log(`  材质 [${idx + 1}]:`, mat.type, mat.name || '未命名')
              
              if ((mat as any).map || (mat as any).albedoMap) {
                hasTextures = true
              }
              
              if (hasVertexColors) {
                console.log('  启用材质的vertexColors')
                ;(mat as any).vertexColors = true
                
                if (mat instanceof THREE.MeshStandardMaterial || 
                    mat instanceof THREE.MeshPhysicalMaterial) {
                  if (!mat.map && !mat.roughnessMap && !mat.normalMap && !mat.metalnessMap) {
                    console.log('  材质没有纹理贴图，将颜色设置为白色以确保顶点颜色正确显示')
                    mat.color.setHex(0xffffff)
                  }
                }
              }
              
              mat.transparent = mat.opacity < 1.0
              mat.depthWrite = !mat.transparent
              
              processMaterial(mat)
            })
          }
        }
      })
      
      console.log('\n=== 遍历完成 ===')
      console.log('网格总数:', meshCount)
      console.log('材质总数:', materialCount)
      console.log('材质类型:', Array.from(materialTypes))
      console.log('有纹理贴图:', hasTextures)
      
      debugInfo.value = {
        modelName: url.split('/').pop() || 'unknown',
        materialCount,
        meshCount,
        hasTextures,
        materialTypes: Array.from(materialTypes)
      }
      
      const box = new THREE.Box3().setFromObject(model)
      const center = box.getCenter(new THREE.Vector3())
      const size = box.getSize(new THREE.Vector3())
      
      console.log('\n模型尺寸:', size)
      console.log('模型中心:', center)

      model.position.sub(center)
      
      const maxDim = Math.max(size.x, size.y, size.z)
      const minDim = Math.min(size.x, size.y, size.z)
      
      let scale = 2 / maxDim
      
      if (minDim < 0.1) {
        scale = Math.min(scale, 10)
      }
      
      model.scale.setScalar(scale)
      
      const scaledSizeY = size.y * scale
      model.position.y += scaledSizeY / 2
      
      console.log('模型缩放:', scale)
      console.log('模型最终位置:', model.position)

      scene.add(model)
      loading.value = false
      emit('loaded')
      
      console.log('\n=== 最终模型信息 ===')
      console.log('模型缩放:', scale)
      console.log('模型位置:', model.position)
    },
    (progress) => {
      if (progress.total > 0) {
        const percent = (progress.loaded / progress.total * 100).toFixed(1)
        console.log(`加载进度: ${percent}%`)
      }
    },
    (err) => {
      console.error('模型加载失败:', err)
      error.value = '模型加载失败: ' + (err as Error).message
      createPlaceholderHuman()
      emit('error', '模型加载失败')
    }
  )
}

const animate = () => {
  animationId = requestAnimationFrame(animate)

  if (controls) {
    controls.update()
  }

  if (renderer && scene && camera) {
    renderer.render(scene, camera)
  }
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

  if (controls) {
    controls.dispose()
  }

  if (renderer) {
    renderer.dispose()
    if (renderer.domElement.parentNode) {
      renderer.domElement.parentNode.removeChild(renderer.domElement)
    }
  }

  if (scene) {
    scene.traverse((child) => {
      const mesh = child as THREE.Mesh
      if (mesh.isMesh) {
        if (mesh.geometry) {
          mesh.geometry.dispose()
        }
        if (mesh.material) {
          if (Array.isArray(mesh.material)) {
            mesh.material.forEach(mat => {
              const matAny = mat as any
              if (matAny.map) matAny.map.dispose()
              if (matAny.normalMap) matAny.normalMap.dispose()
              if (matAny.roughnessMap) matAny.roughnessMap.dispose()
              if (matAny.metalnessMap) matAny.metalnessMap.dispose()
              if (matAny.emissiveMap) matAny.emissiveMap.dispose()
              if (matAny.aoMap) matAny.aoMap.dispose()
              mat.dispose()
            })
          } else {
            const matAny = mesh.material as any
            if (matAny.map) matAny.map.dispose()
            if (matAny.normalMap) matAny.normalMap.dispose()
            if (matAny.roughnessMap) matAny.roughnessMap.dispose()
            if (matAny.metalnessMap) matAny.metalnessMap.dispose()
            if (matAny.emissiveMap) matAny.emissiveMap.dispose()
            if (matAny.aoMap) matAny.aoMap.dispose()
            mesh.material.dispose()
          }
        }
      }
    })
  }

  scene = null
  camera = null
  renderer = null
  controls = null
  model = null
})

watch(() => props.modelUrl, (newUrl, oldUrl) => {
  console.log('modelUrl 变化:', oldUrl, '->', newUrl)
  if (newUrl !== oldUrl) {
    loading.value = true
    error.value = null
    if (newUrl) {
      loadModel(newUrl)
    } else {
      if (model && scene) {
        scene.remove(model)
        model = null
      }
      createPlaceholderHuman()
    }
  }
})

watch(() => props.backgroundColor, () => {
  if (scene) {
    scene.background = backgroundColor.value
  }
})

watch(() => props.autoRotate, (newVal) => {
  console.log('autoRotate 变更:', newVal)
  if (controls) {
    controls.autoRotate = newVal
    controls.update()
  }
})

watch(() => props.wireframe, (newVal) => {
  if (model && scene) {
    scene.remove(model)
    model = null
    
    if (props.modelUrl && !error.value) {
      loading.value = true
      loadModel(props.modelUrl)
    } else {
      createPlaceholderHuman()
    }
  }
})
</script>

<style scoped>
.three-d-viewer {
  width: 100%;
  height: 100%;
  min-height: 300px;
  position: relative;
  overflow: hidden;
}

.three-d-viewer.full-height {
  height: 100%;
}

.three-d-viewer :deep(canvas) {
  display: block;
  width: 100%;
  height: 100%;
}

.loading-overlay,
.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background-color: rgba(250, 247, 242, 0.9);
  z-index: 10;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #E8D5C4;
  border-top-color: #8B6F4E;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}
</style>
