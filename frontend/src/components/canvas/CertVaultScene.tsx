"use client";

import { useFrame } from "@react-three/fiber";
import { useRef } from "react";
import * as THREE from "three";

export function CertVaultScene() {
  const vaultRef = useRef<THREE.Group>(null);

  useFrame((_, delta) => {
    if (vaultRef.current) {
      vaultRef.current.rotation.y += delta * 0.16;
      vaultRef.current.rotation.x = 0.15;
    }
  });

  const plaques: Array<[number, number, number]> = [
    [-1.2, 0.8, 0],
    [0, 0.8, 0],
    [1.2, 0.8, 0],
    [-1.2, -0.6, 0],
    [0, -0.6, 0],
    [1.2, -0.6, 0],
  ];

  return (
    <group ref={vaultRef} position={[1.8, 0.1, -1.8]}>
      {plaques.map((pos, idx) => (
        <mesh key={idx} position={pos}>
          <boxGeometry args={[0.85, 1.05, 0.08]} />
          <meshStandardMaterial
            color={idx % 2 === 0 ? "#06B6D4" : "#10B981"}
            emissive={idx % 2 === 0 ? "#06B6D4" : "#10B981"}
            emissiveIntensity={0.25}
            wireframe
          />
        </mesh>
      ))}
    </group>
  );
}

