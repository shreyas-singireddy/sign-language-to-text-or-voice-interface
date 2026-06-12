# Spec-Kit: Body Tracking Subsystem

## 1. Purpose
The Body Tracking Subsystem extracts upper body/torso skeletal structures, tracking shoulders, elbows, and wrists to normalize hand coordinates.

## 2. Requirements
- **REQ-BT-001**: Track upper-body skeletal landmarks utilizing MediaPipe Pose.
- **REQ-BT-002**: Compute shoulder width parameters to normalize hand landmark coordinates relative to body scale.

## 3. Architecture
- **Inference Engine**: MediaPipe Pose model.
- **Input**: RGB video stream frames.
- **Output**: 33 3D skeletal landmarks.

## 4. Acceptance Criteria
- Shoulders must be detected when user is seated 1–2 meters in front of the camera.
- Shoulder coordinates must scale hand coordinates correctly to ensure cross-device consistency.

## 5. Performance Targets
- Torso coordinate scaling latency: <= 15ms.

## 6. Security Considerations
- Coordinates represent abstract body frames; no biometrics or body shapes are stored.

## 7. Risks
- Loose clothing can alter skeletal landmark positions. Normalizers must use moving averages to smooth coordinate drift.

## 8. Test Cases
- **Test-BT-1**: Validate shoulder-width scaling calculation.
- **Test-BT-2**: Test landmark normalizer output structure.

## 9. Verification Procedures
1. Run pytest suite:
   ```bash
   pytest tests/test_scaffolding.py -k "test_landmark_normalizer"
   ```
