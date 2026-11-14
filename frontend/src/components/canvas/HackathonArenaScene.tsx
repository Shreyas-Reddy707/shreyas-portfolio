"use client";

import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";

export function HackathonArenaScene() {
  const arenaRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (arenaRef.current) {
      arenaRef.current.rotation.y += delta * 0.2;
    }
  });

  return (
    <group ref={arenaRef} position={[1.9, 0.1, -1.5]}>
      <mesh position={[-1.1, 0.4, 0]}>
        <dodecahedronGeometry args={[0.9, 0]} />
        <meshStandardMaterial color="#06B6D4" emissive="#06B6D4" emissiveIntensity={0.3} wireframe />
      </mesh>
      <mesh position={[1.1, -0.3, -0.6]}>
        <dodecahedronGeometry args={[0.85, 0]} />
        <meshStandardMaterial color="#10B981" emissive="#10B981" emissiveIntensity={0.3} wireframe />
      </mesh>
      <mesh position={[0, 0.9, -1.2]}>
        <dodecahedronGeometry args={[0.7, 0]} />
        <meshStandardMaterial color="#38BDF8" emissive="#38BDF8" emissiveIntensity={0.3} wireframe />
      </mesh>
    </group>
  );
}

