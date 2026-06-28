import { useEffect, useRef } from "react";

export default function WebGLBackground() {
  const canvasRef = useRef<HTMLCanvasElement | null>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const gl = canvas.getContext("webgl");
    if (!gl) {
      console.warn("WebGL not supported by this browser.");
      return;
    }

    // Set canvas dimensions
    const resizeCanvas = () => {
      if (!canvas) return;
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      gl.viewport(0, 0, canvas.width, canvas.height);
    };
    resizeCanvas();
    window.addEventListener("resize", resizeCanvas);

    // Vertex Shader Source (simply maps clip space)
    const vsSource = `
      attribute vec2 position;
      void main() {
        gl_Position = vec4(position, 0.0, 1.0);
      }
    `;

    // Fragment Shader Source (morphing liquid streaks)
    const fsSource = `
      precision mediump float;
      uniform float u_time;
      uniform vec2 u_resolution;

      void main() {
        vec2 uv = gl_FragCoord.xy / u_resolution.xy;
        vec2 p = uv - 0.5;
        p.x *= u_resolution.x / u_resolution.y;
        
        float t = u_time * 0.35;
        
        // Accumulate sine and cosine waves for the liquid ripple effect
        float strength = 0.0;
        for (float i = 1.0; i < 4.0; i += 1.0) {
          p.x += sin(p.y * i * 1.5 + t) * 0.2 / i;
          p.y += cos(p.x * i * 1.5 + t) * 0.2 / i;
          strength += abs(0.015 / p.x);
        }
        
        // Sophisticated colors: dark slate, brand electric blue, and deep purple
        vec3 col1 = vec3(0.03, 0.06, 0.15); // Rich slate deep blue
        vec3 col2 = vec3(0.12, 0.29, 0.75); // Electric Blue
        vec3 col3 = vec3(0.24, 0.08, 0.42); // Deep Purple
        
        // Base mix of elegant gradients
        vec3 color = mix(col1, col2, uv.x + sin(t * 0.5) * 0.15);
        color = mix(color, col3, uv.y + cos(t * 0.5) * 0.15);
        
        // Glow highlights
        color += col2 * (strength * 0.04);
        
        // Vignette to darken edges for enhanced text readability
        float vignette = 1.0 - dot(uv - 0.5, uv - 0.5) * 1.6;
        color *= clamp(vignette, 0.2, 1.0) * 0.55;
        
        gl_FragColor = vec4(color, 1.0);
      }
    `;

    // Compile Shader function
    const compileShader = (source: string, type: number) => {
      const shader = gl.createShader(type);
      if (!shader) return null;
      gl.shaderSource(shader, source);
      gl.compileShader(shader);
      if (!gl.getShaderParameter(shader, gl.COMPILE_STATUS)) {
        console.error("Shader compilation error:", gl.getShaderInfoLog(shader));
        gl.deleteShader(shader);
        return null;
      }
      return shader;
    };

    const vertexShader = compileShader(vsSource, gl.VERTEX_SHADER);
    const fragmentShader = compileShader(fsSource, gl.FRAGMENT_SHADER);

    if (!vertexShader || !fragmentShader) return;

    // Link Program
    const program = gl.createProgram();
    if (!program) return;
    gl.attachShader(program, vertexShader);
    gl.attachShader(program, fragmentShader);
    gl.linkProgram(program);

    if (!gl.getProgramParameter(program, gl.LINK_STATUS)) {
      console.error("Program linking error:", gl.getProgramInfoLog(program));
      return;
    }

    gl.useProgram(program);

    // Setup Quad vertices
    const vertices = new Float32Array([
      -1, -1,
       1, -1,
      -1,  1,
      -1,  1,
       1, -1,
       1,  1,
    ]);

    const buffer = gl.createBuffer();
    gl.bindBuffer(gl.ARRAY_BUFFER, buffer);
    gl.bufferData(gl.ARRAY_BUFFER, vertices, gl.STATIC_DRAW);

    const positionLoc = gl.getAttribLocation(program, "position");
    gl.enableVertexAttribArray(positionLoc);
    gl.vertexAttribPointer(positionLoc, 2, gl.FLOAT, false, 0, 0);

    // Uniform locations
    const timeLoc = gl.getUniformLocation(program, "u_time");
    const resolutionLoc = gl.getUniformLocation(program, "u_resolution");

    let animationId: number;
    const startTime = Date.now();

    const render = () => {
      if (!canvas) return;
      const elapsedTime = (Date.now() - startTime) / 1000;

      // Clear
      gl.clearColor(0.05, 0.05, 0.05, 1.0);
      gl.clear(gl.COLOR_BUFFER_BIT);

      // Set Uniforms
      gl.uniform1f(timeLoc, elapsedTime);
      gl.uniform2f(resolutionLoc, canvas.width, canvas.height);

      // Draw
      gl.drawArrays(gl.TRIANGLES, 0, 6);

      animationId = requestAnimationFrame(render);
    };

    render();

    return () => {
      window.removeEventListener("resize", resizeCanvas);
      cancelAnimationFrame(animationId);
      gl.deleteProgram(program);
      gl.deleteShader(vertexShader);
      gl.deleteShader(fragmentShader);
      gl.deleteBuffer(buffer);
    };
  }, []);

  return (
    <canvas
      ref={canvasRef}
      id="webgl-bg-canvas"
      className="absolute inset-0 w-full h-full object-cover pointer-events-none z-0 opacity-85"
    />
  );
}
