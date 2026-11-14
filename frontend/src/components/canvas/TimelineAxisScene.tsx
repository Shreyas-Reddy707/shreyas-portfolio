"use client";

import { useFrame } from "@react-three/fiber";
import { useMemo, useRef } from "react";
import * as THREE from "three";

export function TimelineAxisScene() {
  const groupRef = useRef<THREE.Group>(null);

  const spineGeom = useMemo(() => {
    const pts = [new THREE.Vector3(0, 0, 2), new THREE.Vector3(0, 0, -10)];
    return new THREE.BufferGeometry().setFromPoints(pts);
  }, []);

  useFrame((state) => {
    if (groupRef.current) {
      groupRef.current.rotation.z = Math.sin(state.clock.elapsedTime * 0.3) * 0.08;
    }
  });

  const milestones: Array<{ z: number; color: string; scale: number }> = [
    { z: 0, color: "#06B6D4", scale: 0.75 },
    { z: -3.2, color: "#10B981", scale: 0.65 },
    { z: -6.4, color: "#38BDF8", scale: 0.55 },
  ];

  return (
    <group ref={groupRef} position={[1.8, -0.2, -1]}>
      <lineSegments geometry={spineGeom}>
        <lineBasicMaterial color="#1E293B" />
      </lineSegments>
      {milestones.map((m, idx) => (
        <mesh key={idx} position={[0, 0, m.z]} scale={m.scale}>
          <torusGeometry args={[1.1, 0.04, 12, 48]} />
          <meshStandardMaterial
            color={m.color}
            emissive={m.color}
            emissiveIntensity={0.4}
            wireframe
          />
        </mesh>
      ))}
    </group>
  );
}

