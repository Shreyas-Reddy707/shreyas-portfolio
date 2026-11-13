"use client";

import { AdaptiveDpr, AdaptiveEvents, View } from "@react-three/drei";
import { Canvas, useFrame } from "@react-three/fiber";
import { usePathname } from "next/navigation";
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { CertVaultScene } from "./CertVaultScene";
import { HackathonArenaScene } from "./HackathonArenaScene";
import { NeuralHubScene } from "./NeuralHubScene";
import { ProjectBlueprintsScene } from "./ProjectBlueprintsScene";
import { SceneErrorBoundary } from "./SceneErrorBoundary";
import { TimelineAxisScene } from "./TimelineAxisScene";

function ActiveRouteScene({ pathname }: { pathname: string }) {
  let scene = <NeuralHubScene />;
  if (pathname.startsWith("/projects")) scene = <ProjectBlueprintsScene />;
  else if (pathname.startsWith("/experience")) scene = <TimelineAxisScene />;
  else if (pathname.startsWith("/hackathons")) scene = <HackathonArenaScene />;
  else if (pathname.startsWith("/certificates")) scene = <CertVaultScene />;

  return (
    <View className="absolute inset-0 h-full w-full pointer-events-none">
      {scene}
    </View>
  );
}

function CyberGridFloor() {
  const gridRef = useRef<THREE.GridHelper>(null);

  useFrame(({ clock, pointer }) => {
    if (gridRef.current) {
      gridRef.current.position.z = (clock.getElapsedTime() * 0.4) % 2;
      gridRef.current.rotation.y = pointer.x * 0.05;
    }
  });

  return (
    <gridHelper
      ref={gridRef}
      args={[40, 40, "#00F0FF", "#1E293B"]}
      position={[0, -3.2, 0]}
    />
  );
}

function ParticleField() {
  const pointsRef = useRef<THREE.Points>(null);

  const [positions] = useState(() => {
    const pos = new Float32Array(160 * 3);
    for (let i = 0; i < 160 * 3; i += 3) {
      pos[i] = (Math.random() - 0.5) * 18;
      pos[i + 1] = (Math.random() - 0.5) * 14;
      pos[i + 2] = (Math.random() - 0.5) * 12;
    }
    return pos;
  });

  useFrame(({ clock, pointer }) => {
    if (pointsRef.current) {
      pointsRef.current.rotation.y = clock.getElapsedTime() * 0.03 + pointer.x * 0.12;
      pointsRef.current.rotation.x = -pointer.y * 0.08;
    }
  });

  return (
    <points ref={pointsRef}>
      <bufferGeometry>
        <bufferAttribute
          attach="attributes-position"
          args={[positions, 3]}
        />
      </bufferGeometry>
      <pointsMaterial
        size={0.045}
        color="#00F0FF"
        transparent
        opacity={0.45}
        sizeAttenuation
      />
    </points>
  );
}

function CameraRig() {
  useFrame(({ camera, pointer }) => {
    camera.position.x = THREE.MathUtils.lerp(camera.position.x, pointer.x * 0.5, 0.04);
    camera.position.y = THREE.MathUtils.lerp(camera.position.y, pointer.y * 0.35, 0.04);
  });
  return null;
}

export function PersistentCanvas() {
  const rawPathname = usePathname();
  const pathname = rawPathname || "/";
  const [isHidden, setIsHidden] = useState(false);

  useEffect(() => {
    const onVisibilityChange = () => {
      setIsHidden(document.hidden);
    };
    onVisibilityChange();
    document.addEventListener("visibilitychange", onVisibilityChange);
    return () => {
      document.removeEventListener("visibilitychange", onVisibilityChange);
    };
  }, []);

  useEffect(() => {
    // Immediate cold-load kickstart
    if (typeof window !== "undefined") {
      window.dispatchEvent(new Event("resize"));
      window.dispatchEvent(
        new CustomEvent("portfolio:active-layer", {
          detail: { projectSlug: "securerag", layerIndex: 0 },
        })
      );
    }
  }, [pathname]);

  return (
    <SceneErrorBoundary>
      <div
        aria-hidden="true"
        className="pointer-events-none fixed inset-0 z-0 opacity-80"
      >
        <ActiveRouteScene pathname={pathname} />
        <Canvas
          dpr={[1, 1.5]}
          frameloop={isHidden ? "never" : "always"}
          camera={{ position: [0, 0, 6.5], fov: 48 }}
          gl={{ antialias: true, powerPreference: "high-performance", alpha: true }}
          onCreated={(state) => {
            state.invalidate();
            if (typeof window !== "undefined") {
              window.dispatchEvent(new Event("resize"));
            }
          }}
        >
          <ambientLight intensity={0.5} />
          <pointLight position={[6, 6, 6]} intensity={1.4} color="#00F0FF" />
          <pointLight position={[-6, -4, 4]} intensity={0.9} color="#10B981" />
          <CyberGridFloor />
          <ParticleField />
          <CameraRig />
          <View.Port />
          <AdaptiveDpr pixelated />
          <AdaptiveEvents />
        </Canvas>
      </div>
    </SceneErrorBoundary>
  );
}
