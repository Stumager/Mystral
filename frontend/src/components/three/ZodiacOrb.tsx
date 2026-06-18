import { useEffect, useRef } from "react";
import * as THREE from "three";

interface ZodiacOrbProps {
  sign: string;
  symbol: string;
}

export function ZodiacOrb({ sign, symbol }: ZodiacOrbProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true });
    renderer.setSize(280, 280);
    renderer.setPixelRatio(window.devicePixelRatio);
    renderer.setClearColor(0x000000, 0);

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(60, 1, 0.1, 100);
    camera.position.z = 4;

    // Stars
    const starPositions = new Float32Array(120 * 3);
    for (let i = 0; i < starPositions.length; i++) {
      starPositions[i] = (Math.random() - 0.5) * 20;
    }
    const starGeo = new THREE.BufferGeometry();
    starGeo.setAttribute("position", new THREE.BufferAttribute(starPositions, 3));
    const stars = new THREE.Points(
      starGeo,
      new THREE.PointsMaterial({ color: 0xffffff, size: 0.05, opacity: 0.6, transparent: true })
    );
    scene.add(stars);

    // Orb
    const orb = new THREE.Mesh(
      new THREE.SphereGeometry(1, 32, 32),
      new THREE.MeshStandardMaterial({ color: 0x6b4eff, emissive: 0x3d1e8c })
    );
    scene.add(orb);

    // Ring 1 + dot
    const ring1 = new THREE.Mesh(
      new THREE.TorusGeometry(1.6, 0.008, 2, 80),
      new THREE.MeshBasicMaterial({ color: 0x9b8aff, opacity: 0.4, transparent: true })
    );
    const dot1 = new THREE.Mesh(
      new THREE.SphereGeometry(0.06),
      new THREE.MeshBasicMaterial({ color: 0x9b8aff })
    );
    dot1.position.set(1.6, 0, 0);
    ring1.add(dot1);
    scene.add(ring1);

    // Ring 2 + dot
    const ring2 = new THREE.Mesh(
      new THREE.TorusGeometry(2.2, 0.006, 2, 80),
      new THREE.MeshBasicMaterial({ color: 0xc9a84c, opacity: 0.25, transparent: true })
    );
    const dot2 = new THREE.Mesh(
      new THREE.SphereGeometry(0.05),
      new THREE.MeshBasicMaterial({ color: 0xc9a84c })
    );
    dot2.position.set(2.2, 0, 0);
    ring2.add(dot2);
    scene.add(ring2);

    // Lights
    scene.add(new THREE.AmbientLight(0xffffff, 0.3));
    const pointLight = new THREE.PointLight(0x9b8aff, 2);
    pointLight.position.set(0, 0, 3);
    scene.add(pointLight);

    // Animation
    let animId: number;
    const startTime = performance.now();

    function animate() {
      animId = requestAnimationFrame(animate);
      const t = performance.now() - startTime;

      ring1.rotation.z += 0.004;
      ring2.rotation.z -= 0.002;
      orb.rotation.y += 0.003;
      camera.position.y = Math.sin(t * 0.0008) * 0.15;

      renderer.render(scene, camera);
    }

    animate();

    return () => {
      cancelAnimationFrame(animId);
      renderer.dispose();
    };
  }, []);

  return (
    <div className="relative" style={{ width: 280, height: 280 }}>
      <canvas ref={canvasRef} />
      <div
        className="absolute inset-0 flex items-center justify-center pointer-events-none"
        style={{
          zIndex: 10,
          fontFamily: "'Cormorant Garamond', Georgia, serif",
          fontSize: 56,
          color: "#F0EAFF",
        }}
        aria-label={sign}
      >
        {symbol}
      </div>
    </div>
  );
}
