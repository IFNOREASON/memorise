<template>
  <div class="w-full h-full">
    <svg ref="svgRef" :width="svgWidth" :height="svgHeight" class="cursor-grab"
      @mousedown="startDrag"
      @mousemove="onDrag"
      @mouseup="endDrag"
      @mouseleave="endDrag"
      @wheel.prevent="handleWheel">
      <g :transform="transform">
        <g class="links">
          <path v-for="link in visibleLinks" :key="`link-${link.source.id}-${link.target.id}`" 
            :d="link.path"
            fill="none"
            stroke="#c4b5a3"
            stroke-width="1.5"
            stroke-linecap="round" />
        </g>
        <g class="nodes">
          <g v-for="node in visibleNodes" :key="node.id" 
            :transform="`translate(${node.x}, ${node.y})`"
            class="cursor-pointer"
            @click="handleNodeClick(node)"
            @contextmenu.prevent="handleContextMenu(node, $event)">
            
            <rect :width="nodeWidth" 
              :height="nodeHeight"
              :x="-nodeWidth / 2"
              :y="-nodeHeight / 2"
              :rx="12"
              :fill="node.fill"
              :stroke="node.stroke"
              stroke-width="2"
              class="transition-all duration-200" />
            
            <circle :cx="-nodeWidth/2 + 28" :cy="0" :r="18"
              :fill="node.gender === 'male' ? '#dbeafe' : '#fce7f3'" />
            
            <text :x="-nodeWidth/2 + 28" :y="5" 
              text-anchor="middle"
              :fill="node.gender === 'male' ? '#1d4ed8' : '#db2777'"
              font-size="16">
              {{ node.gender === 'male' ? '♂' : '♀' }}
            </text>
            
            <text :x="-nodeWidth/2 + 52" :y="-6"
              font-size="14"
              font-weight="600"
              :fill="node.deceased ? '#9ca3af' : '#1f2937'">
              {{ node.name }}
            </text>
            
            <text v-if="node.years" :x="-nodeWidth/2 + 52" :y="12"
              font-size="11"
              fill="#6b7280">
              {{ node.years }}
            </text>
            
            <text v-else :x="-nodeWidth/2 + 52" :y="12"
              font-size="11"
              fill="#6b7280">
              第{{ node.generation }}世
            </text>
            
            <g v-if="node.hasChildren" class="cursor-pointer" @click.stop="toggleNode(node)">
              <circle :cx="nodeWidth/2 - 16" :cy="0" :r="12" fill="#e8d5c4" />
              <text :x="nodeWidth/2 - 16" :y="4" 
                text-anchor="middle"
                fill="#8b6f4e"
                font-size="14"
                font-weight="bold">
                {{ node.collapsed ? '+' : '-' }}
              </text>
            </g>
          </g>
        </g>
      </g>
    </svg>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import * as d3 from 'd3'

interface TreeNode {
  id: string
  name: string
  gender: 'male' | 'female'
  generation: number
  birthYear?: string
  deathYear?: string
  spouse?: string
  fatherId?: string
  status: 'alive' | 'deceased'
  x: number
  y: number
  fill: string
  stroke: string
  deceased: boolean
  hasChildren: boolean
  collapsed: boolean
  years: string
  children: TreeNode[]
  parent?: TreeNode
}

interface TreeLink {
  source: TreeNode
  target: TreeNode
  path: string
}

interface FamilyMember {
  id: string
  name: string
  gender: 'male' | 'female'
  generation: number
  birthYear?: string
  deathYear?: string
  spouse?: string
  fatherId?: string
  residence?: string
  note?: string
  status: 'alive' | 'deceased'
}

const props = defineProps<{
  data: FamilyMember[]
  selectedId?: string
  scale?: number
}>()

const emit = defineEmits<{
  (e: 'select', member: FamilyMember): void
  (e: 'context-menu', member: FamilyMember, event: MouseEvent): void
}>()

const svgRef = ref<SVGSVGElement | null>(null)
const svgWidth = ref(1200)
const svgHeight = ref(600)
const nodeWidth = 180
const nodeHeight = 60

const translateX = ref(100)
const translateY = ref(80)
const internalScale = ref(1)
const minScale = 0.3
const maxScale = 2.5

const isDragging = ref(false)
const dragStart = ref({ x: 0, y: 0 })

const collapsedNodes = ref<Set<string>>(new Set())
const treeNodes = ref<TreeNode[]>([])
const treeLinks = ref<{ source: TreeNode; target: TreeNode }[]>([])

const transform = computed(() => {
  const scaleVal = (props.scale || 1) * internalScale.value
  return `translate(${translateX.value}, ${translateY.value}) scale(${scaleVal})`
})

const buildTree = () => {
  if (props.data.length === 0) {
    treeNodes.value = []
    treeLinks.value = []
    return
  }
  
  const memberMap = new Map<string, TreeNode>()
  
  props.data.forEach(m => {
    memberMap.set(m.id, {
      ...m,
      x: 0,
      y: 0,
      fill: '#ffffff',
      stroke: '#e5e7eb',
      deceased: m.status === 'deceased',
      hasChildren: false,
      collapsed: false,
      years: '',
      children: []
    })
  })
  
  const roots: TreeNode[] = []
  
  props.data.forEach(m => {
    const node = memberMap.get(m.id)!
    
    const years: string[] = []
    if (m.birthYear) years.push(m.birthYear)
    if (m.deathYear) years.push(m.deathYear)
    node.years = years.length > 0 ? years.join(' - ') : ''
    
    if (m.fatherId && memberMap.has(m.fatherId)) {
      const parent = memberMap.get(m.fatherId)!
      parent.children.push(node)
      parent.hasChildren = true
      node.parent = parent
    } else {
      if (!roots.some(r => r.id === node.id)) {
        roots.push(node)
      }
    }
  })
  
  if (roots.length === 0 && props.data.length > 0) {
    const firstGen = Math.min(...props.data.map(m => m.generation))
    props.data.filter(m => m.generation === firstGen).forEach(m => {
      if (!roots.some(r => r.id === m.id)) {
        const node = memberMap.get(m.id)!
        roots.push(node)
      }
    })
  }
  
  if (roots.length === 0) {
    treeNodes.value = []
    treeLinks.value = []
    return
  }
  
  const virtualRoot: TreeNode = {
    id: 'virtual-root',
    name: 'root',
    gender: 'male',
    generation: 0,
    status: 'alive',
    x: 0,
    y: 0,
    fill: '#ffffff',
    stroke: '#e5e7eb',
    deceased: false,
    hasChildren: roots.length > 0,
    collapsed: false,
    years: '',
    children: roots
  }
  
  roots.forEach(r => {
    r.parent = virtualRoot
  })
  
  const hierarchy = d3.hierarchy<TreeNode>(virtualRoot, d => d.children)
  
  const treeLayout = d3.tree<TreeNode>()
    .nodeSize([nodeWidth + 50, nodeHeight + 90])
  
  treeLayout(hierarchy)
  
  const allNodes: TreeNode[] = []
  const allLinks: { source: TreeNode; target: TreeNode }[] = []
  
  hierarchy.each(node => {
    if (node.data.id !== 'virtual-root') {
      node.data.x = node.x || 0
      node.data.y = node.y || 0
      allNodes.push(node.data)
    }
  })
  
  hierarchy.links().forEach(link => {
    if (link.source.data.id !== 'virtual-root' && link.target.data.id !== 'virtual-root') {
      allLinks.push({
        source: link.source.data,
        target: link.target.data
      })
    }
  })
  
  if (allNodes.length > 0) {
    const xValues = allNodes.map(n => n.x)
    const yValues = allNodes.map(n => n.y)
    
    const minX = Math.min(...xValues)
    const maxX = Math.max(...xValues)
    const minY = Math.min(...yValues)
    const maxY = Math.max(...yValues)
    
    svgWidth.value = Math.max(800, maxX - minX + nodeWidth * 3)
    svgHeight.value = Math.max(500, maxY - minY + nodeHeight * 3)
    
    translateX.value = -minX + nodeWidth
    translateY.value = -minY + nodeHeight
  }
  
  treeNodes.value = allNodes
  treeLinks.value = allLinks
}

const isNodeVisible = (node: TreeNode): boolean => {
  let current: TreeNode | undefined = node.parent
  while (current) {
    if (current.id !== 'virtual-root' && collapsedNodes.value.has(current.id)) {
      return false
    }
    current = current.parent
  }
  return true
}

const visibleNodes = computed(() => {
  return treeNodes.value
    .filter(node => isNodeVisible(node))
    .map(node => ({
      ...node,
      collapsed: collapsedNodes.value.has(node.id),
      fill: props.selectedId === node.id ? '#fef3c7' : '#ffffff',
      stroke: props.selectedId === node.id ? '#8b6f4e' : '#e5e7eb'
    }))
})

const isLinkVisible = (link: { source: TreeNode; target: TreeNode }): boolean => {
  const source = treeNodes.value.find(n => n.id === link.source.id)
  if (!source) return false
  
  if (collapsedNodes.value.has(source.id)) {
    return false
  }
  
  let current: TreeNode | undefined = source.parent
  while (current) {
    if (current.id !== 'virtual-root' && collapsedNodes.value.has(current.id)) {
      return false
    }
    current = current.parent
  }
  
  return true
}

const visibleLinks = computed(() => {
  return treeLinks.value
    .filter(link => isLinkVisible(link))
    .map(link => {
      const sx = link.source.x
      const sy = link.source.y + nodeHeight / 2
      const tx = link.target.x
      const ty = link.target.y - nodeHeight / 2
      const midY = (sy + ty) / 2
      
      const path = `M ${sx} ${sy} C ${sx} ${midY}, ${tx} ${midY}, ${tx} ${ty}`
      
      return {
        source: link.source,
        target: link.target,
        path
      }
    })
})

watch(() => props.data, () => {
  nextTick(() => buildTree())
}, { deep: true, immediate: true })

watch(() => props.scale, () => {
  nextTick(() => buildTree())
})

watch(collapsedNodes, () => {
}, { deep: true })

const handleNodeClick = (node: TreeNode) => {
  const member = props.data.find(m => m.id === node.id)
  if (member) {
    emit('select', member)
  }
}

const handleContextMenu = (node: TreeNode, event: MouseEvent) => {
  const member = props.data.find(m => m.id === node.id)
  if (member) {
    emit('context-menu', member, event)
  }
}

const toggleNode = (node: TreeNode) => {
  if (collapsedNodes.value.has(node.id)) {
    collapsedNodes.value.delete(node.id)
  } else {
    collapsedNodes.value.add(node.id)
  }
}

const startDrag = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (target.tagName === 'rect' || target.tagName === 'text' || target.tagName === 'circle') {
    return
  }
  isDragging.value = true
  dragStart.value = { x: event.clientX - translateX.value, y: event.clientY - translateY.value }
}

const onDrag = (event: MouseEvent) => {
  if (!isDragging.value) return
  translateX.value = event.clientX - dragStart.value.x
  translateY.value = event.clientY - dragStart.value.y
}

const endDrag = () => {
  isDragging.value = false
}

const handleWheel = (event: WheelEvent) => {
  const delta = event.deltaY > 0 ? -1 : 1
  const scaleStep = 0.1
  const oldScale = internalScale.value
  
  if (delta > 0) {
    internalScale.value = Math.min(maxScale, oldScale + scaleStep)
  } else {
    internalScale.value = Math.max(minScale, oldScale - scaleStep)
  }
}

const expandAll = () => {
  collapsedNodes.value.clear()
}

const collapseAll = () => {
  collapsedNodes.value.clear()
  treeNodes.value.forEach(node => {
    if (node.hasChildren) {
      collapsedNodes.value.add(node.id)
    }
  })
}

const focusNode = (nodeId: string) => {
  const node = treeNodes.value.find(n => n.id === nodeId)
  if (!node) return
  
  if (node.parent && node.parent.id !== 'virtual-root') {
    let parent = node.parent
    while (parent && parent.id !== 'virtual-root') {
      if (collapsedNodes.value.has(parent.id)) {
        collapsedNodes.value.delete(parent.id)
      }
      parent = parent.parent
    }
  }
  
  if (svgRef.value) {
    const rect = svgRef.value.getBoundingClientRect()
    const containerCenterX = rect.width / 2
    const containerCenterY = rect.height / 2
    
    const currentScale = (props.scale || 1) * internalScale.value
    
    translateX.value = containerCenterX / currentScale - node.x
    translateY.value = containerCenterY / currentScale - node.y
  }
}

defineExpose({
  expandAll,
  collapseAll,
  focusNode
})
</script>
