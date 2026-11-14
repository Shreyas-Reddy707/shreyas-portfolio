"use client";

import { useFrame } from "@react-three/fiber";
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";

export function ProjectBlueprintsScene() {
  const [activeProjectSlug, setActiveProjectSlug] = useState<string>("securerag");
  const [activeVisualizerType, setActiveVisualizerType] = useState<string>("zero_trust_shield_stack");
  const [activeLayer, setActiveLayer] = useState<number>(0);
  const selectedProjectRef = useRef<string>("securerag");

  useEffect(() => {
    selectedProjectRef.current = activeProjectSlug;
  }, [activeProjectSlug]);

  useEffect(() => {
    const handler = (e: Event) => {
      const custom = e as CustomEvent<{
        projectSlug: string;
        layerIndex: number;
        visualizerType?: string;
        selectProject?: boolean;
      }>;
      if (!custom.detail) return;

      const { projectSlug, layerIndex, visualizerType, selectProject } = custom.detail;

      // When switching project selection explicitly:
      if (selectProject && projectSlug && projectSlug !== selectedProjectRef.current) {
        selectedProjectRef.current = projectSlug;
        setActiveProjectSlug(projectSlug);
        setActiveLayer(typeof layerIndex === "number" ? layerIndex : 0);
        if (visualizerType) {
          setActiveVisualizerType(visualizerType);
        }
        return;
      }

      // Accept layer updates only when detail.projectSlug matches the currently selected project
      if (projectSlug && projectSlug === selectedProjectRef.current) {
        if (typeof layerIndex === "number") {
          setActiveLayer(layerIndex);
        }
        if (visualizerType) {
          setActiveVisualizerType(visualizerType);
        }
      }
    };
    window.addEventListener("portfolio:active-layer", handler);
    return () => window.removeEventListener("portfolio:active-layer", handler);
  }, []);

  return (
    <group position={[2.2, 0.2, -1.2]}>
      {activeVisualizerType === "analytics_automl_workbench" ? (
        <NeuralDataCoreVisualizer activeLayer={activeLayer} />
      ) : activeVisualizerType === "site_command_and_muster_sim" ? (
        <SiteBeaconRadarVisualizer activeLayer={activeLayer} />
      ) : activeVisualizerType === "geospatial_crisis_radar" ? (
        <GeodesicGlobeVisualizer activeLayer={activeLayer} />
      ) : activeVisualizerType === "multimodal_corpus_funnel" ? (
        <CorpusFunnelCubeVisualizer activeLayer={activeLayer} />
      ) : activeVisualizerType === "cv_topography_comparator" ? (
        <CvTopographySurfaceVisualizer activeLayer={activeLayer} />
      ) : activeVisualizerType === "ml_model_eval_matrix" ||
        activeVisualizerType === "colab_notebook_workflow" ||
        activeVisualizerType === "architecture_flowchart_dag" ? (
        <CadModuleVisualizer activeLayer={activeLayer} />
      ) : (
        <ZeroTrustShieldStackVisualizer activeLayer={activeLayer} />
      )}
    </group>
  );
}

function CadModuleVisualizer({ activeLayer }: { activeLayer: number }) {
  const meshRef = useRef<THREE.Group>(null);
  useFrame((_, delta) => {
    if (meshRef.current) {
      meshRef.current.rotation.y += delta * 0.25;
      meshRef.current.rotation.x = Math.sin(delta) * 0.1;
    }
  });
  return (
    <group ref={meshRef}>
      <mesh>
        <octahedronGeometry args={[1.4, 0]} />
        <meshBasicMaterial color="#00F0FF" wireframe transparent opacity={0.65} />
      </mesh>
      <mesh scale={[0.65, 0.65, 0.65]}>
        <dodecahedronGeometry args={[1, 0]} />
        <meshStandardMaterial
          color="#8B5CF6"
          emissive="#8B5CF6"
          emissiveIntensity={0.5 + activeLayer * 0.1}
          wireframe
        />
      </mesh>
    </group>
  );
}

// ----------------------------------------------------------------------------
// 1. SecureRAG: 5 Concentric Counter-Rotating Security Shields + Core Icosahedron
// ----------------------------------------------------------------------------
function ZeroTrustShieldStackVisualizer({ activeLayer }: { activeLayer: number }) {
  const groupRef = useRef<THREE.Group>(null);
  const l1Ref = useRef<THREE.Mesh>(null);
  const l2Ref = useRef<THREE.Mesh>(null);
  const l3Ref = useRef<THREE.Mesh>(null);
  const l4Ref = useRef<THREE.Mesh>(null);
  const l5Ref = useRef<THREE.Mesh>(null);

  const refs = [l1Ref, l2Ref, l3Ref, l4Ref, l5Ref];

  useFrame((_, delta) => {
    if (groupRef.current) groupRef.current.rotation.y += delta * 0.15;

    refs.forEach((ref, idx) => {
      if (!ref.current) return;
      const isActive = activeLayer === idx;
      ref.current.rotation.y += delta * (0.2 + idx * 0.08) * (isActive ? 2.5 : 1.0);
      ref.current.rotation.x += delta * 0.06 * (idx % 2 === 0 ? 1 : -1);

      const targetScale = isActive ? 1.25 : 1.0;
      ref.current.scale.lerp(new THREE.Vector3(targetScale, targetScale, targetScale), delta * 4);

      const mat = ref.current.material as THREE.MeshStandardMaterial;
      if (mat) {
        const targetIntensity = isActive ? 0.95 : 0.25;
        mat.emissiveIntensity = THREE.MathUtils.lerp(mat.emissiveIntensity, targetIntensity, delta * 5);
        mat.emissive.set(isActive ? "#00F0FF" : idx % 2 === 0 ? "#06B6D4" : "#A855F7");
      }
    });
  });

  return (
    <group ref={groupRef}>
      <mesh ref={l1Ref}>
        <octahedronGeometry args={[2.2, 1]} />
        <meshStandardMaterial color="#00F0FF" emissive="#00F0FF" wireframe transparent opacity={0.75} />
      </mesh>
      <mesh ref={l2Ref}>
        <icosahedronGeometry args={[1.75, 1]} />
        <meshStandardMaterial color="#A855F7" emissive="#A855F7" wireframe transparent opacity={0.7} />
      </mesh>
      <mesh ref={l3Ref} rotation={[Math.PI / 3, 0, 0]}>
        <torusGeometry args={[1.35, 0.08, 16, 64]} />
        <meshStandardMaterial color="#10B981" emissive="#10B981" wireframe />
      </mesh>
      <mesh ref={l4Ref}>
        <boxGeometry args={[1.1, 1.1, 1.1]} />
        <meshStandardMaterial color="#00F0FF" emissive="#00F0FF" wireframe />
      </mesh>
      <mesh ref={l5Ref}>
        <tetrahedronGeometry args={[0.65, 0]} />
        <meshStandardMaterial color="#EC4899" emissive="#EC4899" wireframe />
      </mesh>
    </group>
  );
}

// ----------------------------------------------------------------------------
// 2. DataMind: 3D Floating Tensor Lattice & Orbiting Data Nodes
// ----------------------------------------------------------------------------
function NeuralDataCoreVisualizer({ activeLayer }: { activeLayer: number }) {
  const groupRef = useRef<THREE.Group>(null);
  const coreRef = useRef<THREE.Mesh>(null);
  const ringRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.2;
      groupRef.current.rotation.z = Math.sin(clock.getElapsedTime() * 0.5) * 0.15;
    }
    if (coreRef.current) {
      coreRef.current.rotation.x += delta * 0.3;
      coreRef.current.rotation.y -= delta * 0.4;
    }
    if (ringRef.current) {
      ringRef.current.rotation.x = Math.PI / 2 + Math.sin(clock.getElapsedTime() * 0.8) * 0.2;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Central Tensor Core */}
      <mesh ref={coreRef}>
        <dodecahedronGeometry args={[1.4, 0]} />
        <meshStandardMaterial
          color="#10B981"
          emissive="#10B981"
          emissiveIntensity={0.6}
          wireframe
        />
      </mesh>
      {/* Outer Orbiting Data Ring */}
      <mesh ref={ringRef}>
        <torusGeometry args={[2.0, 0.05, 16, 80]} />
        <meshStandardMaterial
          color="#00F0FF"
          emissive="#00F0FF"
          emissiveIntensity={0.8}
        />
      </mesh>
      {/* 4 Orbiting Tensor Spheres */}
      {[0, 1, 2, 3].map((i) => {
        const angle = (i * Math.PI) / 2;
        return (
          <mesh key={i} position={[Math.cos(angle) * 2.0, Math.sin(angle) * 0.6, Math.sin(angle) * 2.0]}>
            <sphereGeometry args={[0.18, 16, 16]} />
            <meshStandardMaterial
              color="#A855F7"
              emissive="#A855F7"
              emissiveIntensity={0.8}
            />
          </mesh>
        );
      })}
    </group>
  );
}

// ----------------------------------------------------------------------------
// 3. ConstructPulse: 3D Site Beacon & Scanning Perimeter Rings
// ----------------------------------------------------------------------------
function SiteBeaconRadarVisualizer({ activeLayer }: { activeLayer: number }) {
  const groupRef = useRef<THREE.Group>(null);
  const ring1Ref = useRef<THREE.Mesh>(null);
  const ring2Ref = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (groupRef.current) groupRef.current.rotation.y += delta * 0.25;
    if (ring1Ref.current) ring1Ref.current.rotation.z += delta * 0.6;
    if (ring2Ref.current) ring2Ref.current.rotation.z -= delta * 0.4;
  });

  return (
    <group ref={groupRef}>
      {/* Central Site Beacon Tower */}
      <mesh position={[0, 0, 0]}>
        <cylinderGeometry args={[0.2, 0.6, 2.2, 16]} />
        <meshStandardMaterial color="#F59E0B" emissive="#F59E0B" emissiveIntensity={0.7} wireframe />
      </mesh>
      {/* Scanning Perimeter Rings */}
      <mesh ref={ring1Ref} rotation={[Math.PI / 2.5, 0, 0]}>
        <torusGeometry args={[1.6, 0.04, 16, 64]} />
        <meshStandardMaterial color="#00F0FF" emissive="#00F0FF" emissiveIntensity={0.8} />
      </mesh>
      <mesh ref={ring2Ref} rotation={[-Math.PI / 3, 0, 0]}>
        <torusGeometry args={[2.1, 0.03, 16, 64]} />
        <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={0.7} />
      </mesh>
    </group>
  );
}

// ----------------------------------------------------------------------------
// 4. CrisisPulse: 3D Geodesic Globe Wireframe with Orbital Satellites
// ----------------------------------------------------------------------------
function GeodesicGlobeVisualizer({ activeLayer }: { activeLayer: number }) {
  const globeRef = useRef<THREE.Mesh>(null);
  const orbitRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (globeRef.current) {
      globeRef.current.rotation.y += delta * 0.18;
      globeRef.current.rotation.x = 0.2;
    }
    if (orbitRef.current) {
      orbitRef.current.rotation.y -= delta * 0.35;
    }
  });

  return (
    <group>
      {/* Geodesic Globe */}
      <mesh ref={globeRef}>
        <sphereGeometry args={[1.5, 24, 24]} />
        <meshStandardMaterial color="#00F0FF" emissive="#00F0FF" emissiveIntensity={0.4} wireframe />
      </mesh>
      {/* Orbital Track */}
      <group ref={orbitRef} rotation={[Math.PI / 4, 0, 0]}>
        <mesh>
          <torusGeometry args={[2.2, 0.02, 16, 80]} />
          <meshStandardMaterial color="#EC4899" emissive="#EC4899" emissiveIntensity={0.6} />
        </mesh>
        {/* Orbiting Satellite Node */}
        <mesh position={[2.2, 0, 0]}>
          <boxGeometry args={[0.2, 0.2, 0.2]} />
          <meshStandardMaterial color="#F43F5E" emissive="#F43F5E" emissiveIntensity={1.0} />
        </mesh>
      </group>
    </group>
  );
}

// ----------------------------------------------------------------------------
// 5. telarc: 4 Outer Modality Cubes Streaming into Central Vault
// ----------------------------------------------------------------------------
function CorpusFunnelCubeVisualizer({ activeLayer }: { activeLayer: number }) {
  const groupRef = useRef<THREE.Group>(null);
  const centralRef = useRef<THREE.Mesh>(null);

  useFrame((_, delta) => {
    if (groupRef.current) groupRef.current.rotation.y += delta * 0.15;
    if (centralRef.current) {
      centralRef.current.rotation.x += delta * 0.2;
      centralRef.current.rotation.z += delta * 0.25;
    }
  });

  return (
    <group ref={groupRef}>
      {/* Central Hypercube Vault */}
      <mesh ref={centralRef}>
        <boxGeometry args={[1.2, 1.2, 1.2]} />
        <meshStandardMaterial color="#00F0FF" emissive="#00F0FF" emissiveIntensity={0.7} wireframe />
      </mesh>
      {/* 4 Converging Modality Satellites */}
      {[
        [-1.8, 1.2, 0],
        [1.8, 1.2, 0],
        [-1.8, -1.2, 0],
        [1.8, -1.2, 0],
      ].map((pos, i) => (
        <mesh key={i} position={pos as [number, number, number]}>
          <octahedronGeometry args={[0.35, 0]} />
          <meshStandardMaterial
            color={i % 2 === 0 ? "#A855F7" : "#10B981"}
            emissive={i % 2 === 0 ? "#A855F7" : "#10B981"}
            emissiveIntensity={0.8}
            wireframe
          />
        </mesh>
      ))}
    </group>
  );
}

// ----------------------------------------------------------------------------
// 6. Denoising: 3D Isometric Heightfield Topography Surface
// ----------------------------------------------------------------------------
function CvTopographySurfaceVisualizer({ activeLayer }: { activeLayer: number }) {
  const meshRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    if (!meshRef.current) return;
    const geom = meshRef.current.geometry as THREE.PlaneGeometry;
    const pos = geom.attributes.position;
    const t = clock.getElapsedTime() * 1.5;

    // Amplitude dampens as activeLayer increases (0 = noisy, 3 = smooth)
    const noiseFactor = Math.max(0.08, 0.45 - activeLayer * 0.12);

    for (let i = 0; i < pos.count; i++) {
      const u = pos.getX(i);
      const v = pos.getY(i);
      const z = Math.sin(u * 2.5 + t) * Math.cos(v * 2.5 + t) * noiseFactor;
      pos.setZ(i, z);
    }
    pos.needsUpdate = true;
    meshRef.current.rotation.x = -Math.PI / 3;
    meshRef.current.rotation.z = Math.sin(t * 0.2) * 0.15;
  });

  return (
    <group position={[0, -0.2, 0]}>
      <mesh ref={meshRef}>
        <planeGeometry args={[3.2, 3.2, 24, 24]} />
        <meshStandardMaterial
          color={activeLayer === 3 ? "#10B981" : activeLayer === 0 ? "#F43F5E" : "#00F0FF"}
          emissive={activeLayer === 3 ? "#10B981" : activeLayer === 0 ? "#F43F5E" : "#00F0FF"}
          emissiveIntensity={0.65}
          wireframe
        />
      </mesh>
    </group>
  );
}
