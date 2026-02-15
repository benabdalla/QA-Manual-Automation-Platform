import React, { useState, useEffect } from 'react';
import { Card } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Copy, Loader } from 'lucide-react';

interface Agent {
  id: string;
  name: string;
  model: string;
}

export const GherkinGeneratorCard: React.FC = () => {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [selectedAgent, setSelectedAgent] = useState<string>('');
  const [scenarioInput, setScenarioInput] = useState<string>('');
  const [gherkinOutput, setGherkinOutput] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    fetchAgents();
  }, []);

  const fetchAgents = async () => {
    try {
      const response = await fetch('/api/agents');
      const data = await response.json();
      setAgents(data);
    } catch (error) {
      console.error('Error fetching agents:', error);
    }
  };

  const generateGherkin = async () => {
    if (!selectedAgent || !scenarioInput.trim()) return;

    setLoading(true);
    try {
      const response = await fetch('/api/generate-gherkin', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          agentId: selectedAgent,
          scenario: scenarioInput,
        }),
      });

      const data = await response.json();
      if (data.gherkin) {
        setGherkinOutput(data.gherkin);
      } else {
        alert('Error: ' + (data.error || 'Unknown error'));
      }
    } catch (error) {
      console.error('Error generating Gherkin:', error);
      alert('Failed to generate Gherkin');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(gherkinOutput);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <Card className="p-6">
      <h2 className="text-2xl font-bold mb-4">🥒 Gherkin Scenario Generator</h2>

      <div className="space-y-4">
        {/* Agent Selection */}
        <div>
          <label className="block text-sm font-medium mb-2">Select Agent</label>
          <Select value={selectedAgent} onValueChange={setSelectedAgent}>
            <SelectTrigger>
              <SelectValue placeholder="Choose an agent..." />
            </SelectTrigger>
            <SelectContent>
              {agents.map((agent) => (
                <SelectItem key={agent.id} value={agent.id}>
                  {agent.name} ({agent.model})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        {/* Scenario Input */}
        <div>
          <label className="block text-sm font-medium mb-2">Manual Scenario Description</label>
          <Textarea
            placeholder="Describe your test scenario in plain language..."
            value={scenarioInput}
            onChange={(e) => setScenarioInput(e.target.value)}
            rows={6}
            className="font-mono"
          />
        </div>

        {/* Generate Button */}
        <Button 
          onClick={generateGherkin} 
          disabled={loading || !selectedAgent || !scenarioInput.trim()}
          className="w-full"
        >
          {loading ? <><Loader className="animate-spin mr-2" /> Generating...</> : 'Generate Gherkin'}
        </Button>

        {/* Gherkin Output */}
        {gherkinOutput && (
          <div>
            <label className="block text-sm font-medium mb-2">Gherkin Output</label>
            <Textarea 
              value={gherkinOutput} 
              readOnly 
              rows={10} 
              className="bg-gray-50 font-mono text-sm"
            />
            <Button 
              onClick={copyToClipboard} 
              variant="outline"
              className="mt-2 w-full"
            >
              <Copy className="mr-2 h-4 w-4" />
              {copied ? 'Copied!' : 'Copy to Clipboard'}
            </Button>
          </div>
        )}
      </div>
    </Card>
  );
};
