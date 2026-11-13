"use client";

import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

const PILLAR_NODES: Array<{ pos: [number, number, number]; color: string; scale: number }> = [
  { pos: [0, 0.2, 0], color: "#06B6D4", scale: 0.9 },
  { pos: [-2.4, 0.9, -0.8], color: "#06B6D4", scale: 0.55 },
  { pos: [2.4, 0.7, -0.6], color: "#10B981", scale: 0.55 },
  { pos: [0.2, -1.6, -1.1], color: "#38BDF8", scale: 0.55 },
  { pos: [-1.5, -1.1, 0.5], color: "#10B981", scale: 0.32 },
  { pos: [1.7, -0.9, 0.6], color: "#06B6D4", scale: 0.32 },
];

export function NeuralHubScene() {
  const groupRef = useRef<THREE.Group>(null);
  const ringRef = useRef<THREE.Mesh>(null);

  const lineGeometry = useMemo(() => {
    const points: THREE.Vector3[] = [];
    const center = new THREE.Vector3(...PILLAR_NODES[0].pos);
    for (let i = 1; i < PILLAR_NODES.length; i++) {
      points.push(center, new THREE.Vector3(...PILLAR_NODES[i].pos));
    }
    points.push(
      new THREE.Vector3(...PILLAR_NODES[1].pos),
      new THREE.Vector3(...PILLAR_NODES[2].pos),
      new THREE.Vector3(...PILLAR_NODES[2].pos),
      new THREE.Vector3(...PILLAR_NODES[3].pos),
      new THREE.Vector3(...PILLAR_NODES[3].pos),
      new THREE.Vector3(...PILLAR_NODES[1].pos)
    );
    return new THREE.BufferGeometry().setFromPoints(points);
  }, []);

  useFrame((state, delta) => {
    if (groupRef.current) {
      groupRef.current.rotation.y += delta * 0.14;
      groupRef.current.position.y = Math.sin(state.clock.elapsedTime * 0.6) * 0.12;
    }
    if (ringRef.current) {
      ringRef.current.rotation.z -= delta * 0.2;
      ringRef.current.rotation.x = Math.PI / 3;
    }
  });

  return (
    <group ref={groupRef} position={[1.4, 0, -1]}>
      <lineSegments geometry={lineGeometry}>
        <lineBasicMaterial color="#00F0FF" transparent opacity={0.6} />
      </lineSegments>

      {PILLAR_NODES.map((node, idx) => (
        <mesh key={idx} position={node.pos} scale={node.scale}>
          <icosahedronGeometry args={[1, idx === 0 ? 1 : 0]} />
          <meshStandardMaterial
            color={node.color}
            emissive={node.color}
            emissiveIntensity={0.6}
            wireframe
          />
        </mesh>
      ))}

      <mesh ref={ringRef}>
        <torusGeometry args={[2.9, 0.015, 8, 96]} />
        <meshBasicMaterial color="#00F0FF" transparent opacity={0.5} />
      </mesh>
    </group>
  );
}

