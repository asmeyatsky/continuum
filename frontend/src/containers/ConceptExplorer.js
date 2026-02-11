import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import styled from 'styled-components';
import { FiSend, FiUpload, FiPlay, FiPause, FiSettings, FiGlobe, FiBook, FiClock, FiTarget, FiLoader } from 'react-icons/fi';
import { useSubmitConcept } from '../utils/hooks';

const ExplorerContainer = styled.div`
  max-width: 800px;
  margin: 0 auto;
`;

const Header = styled.div`
  text-align: center;
  margin-bottom: 30px;
`;

const Title = styled.h1`
  font-size: 2rem;
  color: #212529;
  margin-bottom: 10px;
`;

const Subtitle = styled.p`
  color: #6c757d;
  font-size: 1.1rem;
`;

const FormContainer = styled.div`
  background: white;
  border-radius: 12px;
  padding: 30px;
  box-shadow: 0 2px 20px rgba(0,0,0,0.08);
`;

const FormGroup = styled.div`
  margin-bottom: 25px;
`;

const Label = styled.label`
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #495057;
  font-size: 1rem;
`;

const TextArea = styled.textarea`
  width: 100%;
  padding: 12px;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  resize: vertical;
  min-height: 120px;
  font-size: 1rem;
  font-family: inherit;

  &:focus {
    outline: none;
    border-color: #667eea;
    box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
  }
`;

const CheckboxGroup = styled.div`
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  margin-top: 10px;
`;

const CheckboxItem = styled.label`
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  border: 1px solid #e9ecef;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;

  input {
    margin: 0;
  }

  &:hover {
    border-color: #667eea;
    background-color: #f8f9ff;
  }

  ${props => props.checked && `
    border-color: #667eea;
    background-color: #f0f4ff;
  `}
`;

const ButtonGroup = styled.div`
  display: flex;
  gap: 15px;
  margin-top: 20px;
`;

const Button = styled.button`
  flex: 1;
  padding: 14px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;

  ${props => props.variant === 'primary' ? `
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;

    &:hover {
      opacity: 0.9;
    }

    &:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }
  ` : `
    background: white;
    color: #6c757d;
    border: 1px solid #e9ecef;

    &:hover {
      background: #f8f9fa;
    }
  `}
`;

const SliderContainer = styled.div`
  margin: 15px 0;
`;

const SliderLabel = styled.div`
  display: flex;
  justify-content: space-between;
  margin-bottom: 8px;
`;

const Slider = styled.input`
  width: 100%;
  height: 6px;
  border-radius: 3px;
  background: #e9ecef;
  outline: none;
  -webkit-appearance: none;

  &::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 18px;
    height: 18px;
    border-radius: 50%;
    background: #667eea;
    cursor: pointer;
  }
`;

const ErrorBanner = styled.div`
  background: #f8d7da;
  color: #721c24;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 20px;
`;

const ExplorationControls = styled.div`
  background: white;
  border-radius: 12px;
  padding: 20px;
  margin-top: 25px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.05);
`;

const ControlsHeader = styled.h3`
  font-size: 1.1rem;
  color: #495057;
  margin-bottom: 15px;
  display: flex;
  align-items: center;
  gap: 8px;
`;

const ControlGroup = styled.div`
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
  margin-bottom: 15px;
`;

const ConceptExplorer = () => {
  const [concept, setConcept] = useState('');
  const [depth, setDepth] = useState(5);
  const [focusAreas, setFocusAreas] = useState(['research', 'applications']);
  const [isPlaying, setIsPlaying] = useState(false);
  const { submit, loading, error } = useSubmitConcept();
  const navigate = useNavigate();

  const focusOptions = [
    { value: 'research', label: 'Research Papers', icon: <FiBook /> },
    { value: 'applications', label: 'Real-World Applications', icon: <FiGlobe /> },
    { value: 'history', label: 'Historical Context', icon: <FiClock /> },
    { value: 'future', label: 'Future Trends', icon: <FiTarget /> }
  ];

  const handleFocusAreaChange = (value) => {
    if (focusAreas.includes(value)) {
      setFocusAreas(focusAreas.filter(area => area !== value));
    } else {
      setFocusAreas([...focusAreas, value]);
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!concept.trim() || loading) return;

    try {
      const result = await submit(concept.trim());
      if (result?.exploration_id) {
        navigate(`/explore/${result.exploration_id}`);
      }
    } catch (err) {
      // Error is captured in the hook
    }
  };

  return (
    <ExplorerContainer>
      <Header>
        <Title>Explore New Concepts</Title>
        <Subtitle>Describe the concept, idea, or diagram you want to explore</Subtitle>
      </Header>

      {error && (
        <ErrorBanner>
          Failed to start exploration. Please check that the backend is running and try again.
        </ErrorBanner>
      )}

      <FormContainer>
        <form onSubmit={handleSubmit}>
          <FormGroup>
            <Label htmlFor="concept">Concept Description</Label>
            <TextArea
              id="concept"
              value={concept}
              onChange={(e) => setConcept(e.target.value)}
              placeholder="Enter your concept here... e.g., 'sustainable agriculture', 'blockchain technology', or describe an image/diagram"
              required
              disabled={loading}
            />
          </FormGroup>

          <FormGroup>
            <Label>Exploration Depth</Label>
            <SliderContainer>
              <SliderLabel>
                <span>Shallow</span>
                <span>{depth}/10</span>
                <span>Deep</span>
              </SliderLabel>
              <Slider
                type="range"
                min="1"
                max="10"
                value={depth}
                onChange={(e) => setDepth(parseInt(e.target.value))}
              />
            </SliderContainer>
          </FormGroup>

          <FormGroup>
            <Label>Focus Areas</Label>
            <CheckboxGroup>
              {focusOptions.map(option => (
                <CheckboxItem
                  key={option.value}
                  checked={focusAreas.includes(option.value)}
                >
                  <input
                    type="checkbox"
                    checked={focusAreas.includes(option.value)}
                    onChange={() => handleFocusAreaChange(option.value)}
                  />
                  {option.icon}
                  {option.label}
                </CheckboxItem>
              ))}
            </CheckboxGroup>
          </FormGroup>

          <ButtonGroup>
            <Button type="submit" variant="primary" disabled={loading || !concept.trim()}>
              {loading ? <><FiLoader /> Starting...</> : <><FiSend /> Start Exploration</>}
            </Button>
            <Button type="button" variant="secondary">
              <FiUpload /> Upload Diagram/Chart
            </Button>
          </ButtonGroup>
        </form>
      </FormContainer>

      <ExplorationControls>
        <ControlsHeader><FiSettings /> Exploration Controls</ControlsHeader>
        <ControlGroup>
          <Button
            onClick={() => setIsPlaying(!isPlaying)}
            variant={isPlaying ? 'secondary' : 'primary'}
          >
            {isPlaying ? <FiPause /> : <FiPlay />}
            {isPlaying ? 'Pause' : 'Play'}
          </Button>
          <select style={{ padding: '10px', borderRadius: '6px', border: '1px solid #e9ecef' }}>
            <option>Normal Speed</option>
            <option>Fast Speed</option>
            <option>Slow Speed</option>
          </select>
        </ControlGroup>
      </ExplorationControls>
    </ExplorerContainer>
  );
};

export default ConceptExplorer;
