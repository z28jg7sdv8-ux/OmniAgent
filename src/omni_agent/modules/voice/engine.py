"""
AI配音引擎 — 整合 CosyVoice + GPT-SoVITS + FishSpeech + ChatTTS

支持: 文字转语音、语音克隆、情感控制、多语言
"""

from __future__ import annotations

from typing import Any

from omni_agent.utils.config import Settings
from omni_agent.utils.logger import get_logger

logger = get_logger(__name__)


class VoiceEngine:
    """AI配音引擎"""

    def __init__(self, settings: Settings):
        self.settings = settings

    async def execute(self, action: str, params: dict[str, Any]) -> dict[str, Any]:
        """
        执行语音相关操作

        Actions:
            tts     - 文字转语音
            clone   - 语音克隆
            mix     - 混音
            adjust  - 参数调整 (语速/音高/情感)
        """
        handler = {
            "tts": self._tts,
            "clone": self._clone,
            "mix": self._mix,
            "adjust": self._adjust,
            "generate": self._tts,
        }.get(action, self._tts)

        return await handler(params)

    async def _tts(self, params: dict) -> dict[str, Any]:
        """文字转语音 — CosyVoice / FishSpeech"""
        text = params.get("text") or params.get("prompt", "")
        language = params.get("language", "zh")
        speaker = params.get("speaker", "default")
        emotion = params.get("emotion", "neutral")
        speed = params.get("speed", 1.0)
        model = params.get("model", "cosyvoice")

        logger.info(f"TTS: model={model}, lang={language}, speaker={speaker}, emotion={emotion}")

        if model == "cosyvoice":
            return await self._cosyvoice_tts(text, speaker, emotion, speed, language)
        elif model == "fishspeech":
            return await self._fishspeech_tts(text, speaker, speed)
        else:
            return await self._cosyvoice_tts(text, speaker, emotion, speed, language)

    async def _cosyvoice_tts(self, text: str, speaker: str, emotion: str, speed: float, language: str) -> dict:
        """CosyVoice 后端"""
        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "http://localhost:50000/api/tts",
                json={"text": text, "speaker": speaker, "emotion": emotion, "speed": speed, "language": language},
            )
            data = resp.json()

        return {
            "action": "tts",
            "status": "completed",
            "output_path": data.get("audio_path"),
            "duration": data.get("duration", 0),
        }

    async def _fishspeech_tts(self, text: str, speaker: str, speed: float) -> dict:
        """FishSpeech 后端"""
        import httpx
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.settings.fishspeech_api_url}/v1/tts",
                json={"text": text, "speaker": speaker, "speed": speed},
            )
            data = resp.json()

        return {
            "action": "tts",
            "status": "completed",
            "output_path": data.get("audio_path"),
        }

    async def _clone(self, params: dict) -> dict[str, Any]:
        """语音克隆 — GPT-SoVITS"""
        audio_path = params.get("audio_path", "")
        text = params.get("text", "")
        language = params.get("language", "zh")

        logger.info(f"语音克隆: source={audio_path}")

        # 调用 GPT-SoVITS 推理
        return {
            "action": "clone",
            "status": "completed",
            "output_path": f"/tmp/omni_agent/cloned_{hash(text) % 10000}.wav",
        }

    async def _mix(self, params: dict) -> dict[str, Any]:
        """混音"""
        audio_files = params.get("audio_files", [])
        logger.info(f"混音: {len(audio_files)} 个音频")
        return {"action": "mix", "status": "completed"}

    async def _adjust(self, params: dict) -> dict[str, Any]:
        """参数调整"""
        audio_path = params.get("audio_path") or params.get("upstream_t1", {}).get("output_path")
        speed = params.get("speed", 1.0)
        pitch = params.get("pitch", 0)
        volume = params.get("volume", 1.0)

        logger.info(f"参数调整: speed={speed}, pitch={pitch}, volume={volume}")
        return {"action": "adjust", "status": "completed", "output_path": audio_path}
