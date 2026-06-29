import { RefObject, useState } from "react";
import html2canvas from "html2canvas";

export function useShareCard(ref: RefObject<HTMLElement | null>) {
  const [isLoading, setIsLoading] = useState(false);

  async function share() {
    if (!ref.current) return;
    setIsLoading(true);
    try {
      await document.fonts.ready;
      const canvas = await html2canvas(ref.current, {
        scale: 2,
        useCORS: true,
        backgroundColor: "#07060F",
      });
      const dataUrl = canvas.toDataURL("image/png");
      const blob = await (await fetch(dataUrl)).blob();
      const file = new File([blob], "mystral-reading.png", { type: "image/png" });

      if (navigator.share && navigator.canShare?.({ files: [file] })) {
        await navigator.share({ files: [file], title: "Mystral", text: "Мой расклад на Mystral" });
      } else {
        const a = document.createElement("a");
        a.href = dataUrl;
        a.download = "mystral-reading.png";
        a.click();
      }
    } catch (e) {
      console.error("Share failed:", e);
    } finally {
      setIsLoading(false);
    }
  }

  return { share, isLoading };
}
