/**
 * Response Consolidator
 *
 * Post-processes responses from multiple experts to:
 * - Eliminate redundancy
 * - Highlight agreements and differences
 * - Create cohesive, consolidated output
 */

/**
 * Consolidate responses from multiple experts
 */
function consolidateResponses(responses) {
  if (responses.length === 1) {
    return {
      consolidated: responses[0].response,
      experts: [responses[0].expert],
      hasMultipleExperts: false
    };
  }

  // Multi-expert consolidation
  const sections = {
    consensus: extractConsensus(responses),
    differences: extractDifferences(responses),
    recommendations: extractRecommendations(responses),
    implementation: extractImplementationSteps(responses)
  };

  const consolidated = buildConsolidatedOutput(sections, responses);

  return {
    consolidated,
    experts: responses.map(r => r.expert),
    hasMultipleExperts: true,
    sections
  };
}

/**
 * Extract points of consensus across experts
 */
function extractConsensus(responses) {
  const consensus = [];

  // Common keywords/phrases detection
  const allText = responses.map(r => r.response.toLowerCase()).join(' ');

  // Look for repeated recommendations
  const commonPatterns = [
    /use\s+(\w+)/gi,
    /implement\s+(\w+)/gi,
    /consider\s+(\w+)/gi,
    /recommend\s+(\w+)/gi
  ];

  const mentions = new Map();

  commonPatterns.forEach(pattern => {
    let match;
    while ((match = pattern.exec(allText)) !== null) {
      const term = match[1];
      mentions.set(term, (mentions.get(term) || 0) + 1);
    }
  });

  // Extract terms mentioned by multiple experts
  for (const [term, count] of mentions.entries()) {
    if (count >= 2 && term.length > 3) {
      consensus.push(term);
    }
  }

  return consensus;
}

/**
 * Extract differences in expert opinions
 */
function extractDifferences(responses) {
  const differences = [];

  // Simple heuristic: Look for contrasting language
  const contrastIndicators = [
    'however', 'but', 'alternatively', 'instead',
    'on the other hand', 'whereas', 'while'
  ];

  responses.forEach((response, idx) => {
    const text = response.response.toLowerCase();

    contrastIndicators.forEach(indicator => {
      if (text.includes(indicator)) {
        differences.push({
          expert: response.expert,
          context: extractSentenceContaining(response.response, indicator)
        });
      }
    });
  });

  return differences;
}

/**
 * Extract specific recommendations
 */
function extractRecommendations(responses) {
  const recommendations = [];

  responses.forEach(response => {
    const lines = response.response.split('\n');

    lines.forEach(line => {
      // Look for recommendation patterns
      if (
        line.match(/recommend/i) ||
        line.match(/should use/i) ||
        line.match(/best practice/i) ||
        line.match(/✅/i)
      ) {
        recommendations.push({
          expert: response.expert,
          recommendation: line.trim()
        });
      }
    });
  });

  return recommendations;
}

/**
 * Extract implementation steps
 */
function extractImplementationSteps(responses) {
  const steps = [];

  responses.forEach(response => {
    const lines = response.response.split('\n');
    let inStepsList = false;

    lines.forEach(line => {
      const trimmed = line.trim();

      // Detect numbered steps
      if (trimmed.match(/^\d+[\.)]/)) {
        steps.push({
          expert: response.expert,
          step: trimmed
        });
        inStepsList = true;
      } else if (inStepsList && trimmed.match(/^-\s+/)) {
        steps.push({
          expert: response.expert,
          step: trimmed
        });
      } else if (trimmed === '') {
        inStepsList = false;
      }
    });
  });

  return steps;
}

/**
 * Build consolidated output
 */
function buildConsolidatedOutput(sections, responses) {
  const lines = [];

  // Header
  lines.push('# Expert Consultation Summary');
  lines.push('');
  lines.push(`**Consulted Experts**: ${responses.map(r => r.expert).join(', ')}`);
  lines.push('');

  // Consensus section
  if (sections.consensus.length > 0) {
    lines.push('## Key Points of Agreement');
    lines.push('');
    lines.push('All experts agree on:');
    sections.consensus.slice(0, 5).forEach(point => {
      lines.push(`- ${point}`);
    });
    lines.push('');
  }

  // Recommendations
  if (sections.recommendations.length > 0) {
    lines.push('## Recommendations');
    lines.push('');

    // Group by expert
    const byExpert = new Map();
    sections.recommendations.forEach(rec => {
      if (!byExpert.has(rec.expert)) {
        byExpert.set(rec.expert, []);
      }
      byExpert.get(rec.expert).push(rec.recommendation);
    });

    byExpert.forEach((recs, expert) => {
      lines.push(`### From ${expert}`);
      recs.forEach(rec => {
        lines.push(`- ${rec}`);
      });
      lines.push('');
    });
  }

  // Different perspectives
  if (sections.differences.length > 0) {
    lines.push('## Different Perspectives');
    lines.push('');
    sections.differences.forEach(diff => {
      lines.push(`**${diff.expert}**: ${diff.context}`);
      lines.push('');
    });
  }

  // Implementation steps
  if (sections.implementation.length > 0) {
    lines.push('## Implementation Steps');
    lines.push('');

    // Consolidate steps from all experts
    const uniqueSteps = new Set();
    sections.implementation.forEach(s => {
      uniqueSteps.add(s.step);
    });

    Array.from(uniqueSteps).forEach(step => {
      lines.push(step);
    });
    lines.push('');
  }

  // Full responses section
  lines.push('---');
  lines.push('');
  lines.push('## Detailed Expert Responses');
  lines.push('');

  responses.forEach(response => {
    lines.push(`### ${response.expert}`);
    lines.push('');
    lines.push(response.response);
    lines.push('');
    lines.push('---');
    lines.push('');
  });

  return lines.join('\n');
}

/**
 * Extract sentence containing a term
 */
function extractSentenceContaining(text, term) {
  const sentences = text.split(/[.!?]+/);

  const match = sentences.find(s =>
    s.toLowerCase().includes(term.toLowerCase())
  );

  return match ? match.trim() + '.' : '';
}

/**
 * Detect if responses are redundant
 */
function detectRedundancy(responses) {
  if (responses.length < 2) return { hasRedundancy: false };

  const texts = responses.map(r => r.response.toLowerCase());

  // Simple similarity check: common word count
  const words1 = new Set(texts[0].split(/\s+/).filter(w => w.length > 4));
  const words2 = new Set(texts[1].split(/\s+/).filter(w => w.length > 4));

  const intersection = new Set([...words1].filter(w => words2.has(w)));
  const union = new Set([...words1, ...words2]);

  const similarity = intersection.size / union.size;

  return {
    hasRedundancy: similarity > 0.5,
    similarity,
    recommendation: similarity > 0.5
      ? 'Responses are highly similar. Consider using only one expert for this query.'
      : 'Responses provide complementary perspectives.'
  };
}

/**
 * Generate summary statistics
 */
function generateSummary(responses) {
  const totalLength = responses.reduce((sum, r) => sum + r.response.length, 0);
  const avgLength = Math.round(totalLength / responses.length);

  return {
    expertCount: responses.length,
    totalLength,
    avgLength,
    experts: responses.map(r => r.expert)
  };
}

module.exports = {
  consolidateResponses,
  extractConsensus,
  extractDifferences,
  extractRecommendations,
  extractImplementationSteps,
  detectRedundancy,
  generateSummary
};
