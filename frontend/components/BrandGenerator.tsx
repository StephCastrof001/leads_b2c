'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Sparkles, 
  Palette, 
  Type, 
  Image as ImageIcon, 
  Copy, 
  Check, 
  ArrowRight,
  Loader2,
  Sparkles as SparklesIcon
} from 'lucide-react';
import { cn } from '@/lib/utils';

interface CompanyInput {
  company_name: string;
  vision: string;
  mission: string;
  purpose: string;
  values: string[];
  industry: string;
  keywords: string[];
  target_audience: string;
  aesthetic_direction?: string;
  personality?: string;
}

interface BriefResponse {
  brief: string;
  name_suggestions: Array<{
    name: string;
    rationale: string;
  }>;
  brandkit_inputs: Record<string, any>;
  generated_at: string;
}

interface BrandKitResponse {
  palettes: Array<{
    hex: string;
    name: string;
    desc: string;
  }>;
  typography: Array<{
    type: string;
    name: string;
    desc: string;
  }>;
  taglines: {
    en: string;
    es: string;
  };
  logos: string[];
  generated_at: string;
}

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function BrandGenerator() {
  const [step, setStep] = useState<'input' | 'brief' | 'assets'>('input');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [companyInput, setCompanyInput] = useState<CompanyInput>({
    company_name: '',
    vision: '',
    mission: '',
    purpose: '',
    values: [],
    industry: 'SaaS',
    keywords: [],
    target_audience: '',
    aesthetic_direction: 'minimal',
    personality: 'professional'
  });
  const [brief, setBrief] = useState<BriefResponse | null>(null);
  const [brandKit, setBrandKit] = useState<BrandKitResponse | null>(null);
  const [copied, setCopied] = useState<string | null>(null);

  // Phase 1: Generate Brief
  const handleGenerateBrief = async () => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/v1/brief`, companyInput);
      setBrief(response.data);
      setStep('brief');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate brief');
    } finally {
      setLoading(false);
    }
  };

  // Phase 2: Generate Brand Kit
  const handleGenerateBrandKit = async () => {
    if (!brief) return;

    setLoading(true);
    setError(null);

    try {
      const response = await axios.post(`${API_URL}/v1/generate`, {
        brandkit_inputs: brief.brandkit_inputs,
        direction: companyInput.aesthetic_direction || 'minimal',
        style: companyInput.personality || 'modern'
      });
      setBrandKit(response.data);
      setStep('assets');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Failed to generate brand kit');
    } finally {
      setLoading(false);
    }
  };

  // Copy to clipboard
  const copyToClipboard = async (text: string, name: string) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopied(name);
      setTimeout(() => setCopied(null), 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  };

  // Add value
  const addValue = (value: string) => {
    if (!companyInput.values.includes(value)) {
      setCompanyInput({
        ...companyInput,
        values: [...companyInput.values, value]
      });
    }
  };

  // Remove value
  const removeValue = (value: string) => {
    setCompanyInput({
      ...companyInput,
      values: companyInput.values.filter(v => v !== value)
    });
  };

  // Add keyword
  const addKeyword = (keyword: string) => {
    if (!companyInput.keywords.includes(keyword)) {
      setCompanyInput({
        ...companyInput,
        keywords: [...companyInput.keywords, keyword]
      });
    }
  };

  // Remove keyword
  const removeKeyword = (keyword: string) => {
    setCompanyInput({
      ...companyInput,
      keywords: companyInput.keywords.filter(k => k !== keyword)
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-dark-950 via-dark-900 to-dark-800 text-white">
      {/* Header */}
      <header className="border-b border-dark-700/50 backdrop-blur-sm">
        <div className="max-w-7xl mx-auto px-6 py-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <SparklesIcon className="w-8 h-8 text-primary-400" />
            <h1 className="text-2xl font-display font-bold">
              Klipso Brand Forge
            </h1>
          </div>
          <nav className="flex items-center gap-4">
            <span className="text-sm text-dark-400">
              {loading ? 'Processing...' : 'Ready'}
            </span>
          </nav>
        </div>
      </header>

      {/* Progress Steps */}
      <div className="max-w-7xl mx-auto px-6 py-8">
        <div className="flex items-center justify-center gap-4 mb-12">
          {[
            { id: 'input', label: 'Strategy' },
            { id: 'brief', label: 'Brief' },
            { id: 'assets', label: 'Assets' }
          ].map((s, i) => (
            <div key={s.id} className="flex items-center">
              <div
                className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center font-bold transition-all',
                  step === s.id
                    ? 'bg-primary-500 text-white shadow-lg shadow-primary-500/25'
                    : step > s.id
                    ? 'bg-primary-600 text-white'
                    : 'bg-dark-700 text-dark-400'
                )}
              >
                {i + 1}
              </div>
              <span
                className={cn(
                  'ml-2 text-sm font-medium transition-colors',
                  step === s.id ? 'text-white' : 'text-dark-400'
                )}
              >
                {s.label}
              </span>
              {i < 2 && (
                <div className="w-12 h-0.5 bg-dark-700 ml-4" />
              )}
            </div>
          ))}
        </div>

        {/* Step 1: Input */}
        {step === 'input' && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-4xl mx-auto"
          >
            <div className="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700/50">
              <h2 className="text-2xl font-display font-bold mb-6">
                Define Your Brand Vision
              </h2>

              <div className="space-y-6">
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Company Name
                  </label>
                  <input
                    type="text"
                    value={companyInput.company_name}
                    onChange={(e) =>
                      setCompanyInput({
                        ...companyInput,
                        company_name: e.target.value
                      })
                    }
                    className="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="Enter your company name"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-dark-300 mb-2">
                      Vision
                    </label>
                    <textarea
                      value={companyInput.vision}
                      onChange={(e) =>
                        setCompanyInput({
                          ...companyInput,
                          vision: e.target.value
                        })
                      }
                      className="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                      placeholder="Your long-term aspiration"
                      rows={3}
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dark-300 mb-2">
                      Mission
                    </label>
                    <textarea
                      value={companyInput.mission}
                      onChange={(e) =>
                        setCompanyInput({
                          ...companyInput,
                          mission: e.target.value
                        })
                      }
                      className="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                      placeholder="Your purpose-driven action"
                      rows={3}
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Purpose
                  </label>
                  <textarea
                    value={companyInput.purpose}
                    onChange={(e) =>
                      setCompanyInput({
                        ...companyInput,
                        purpose: e.target.value
                      })
                    }
                    className="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    placeholder="Why your brand exists"
                    rows={3}
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Core Values
                  </label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {companyInput.values.map((v) => (
                      <span
                        key={v}
                        className="px-3 py-1 bg-primary-500/20 text-primary-300 rounded-full text-sm flex items-center gap-1"
                      >
                        {v}
                        <button
                          onClick={() => removeValue(v)}
                          className="hover:text-white"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <input
                    type="text"
                    placeholder="Add a value (press Enter)"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        const value = e.currentTarget.value.trim();
                        if (value) {
                          addValue(value);
                          e.currentTarget.value = '';
                        }
                      }
                    }}
                    className="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  />
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-dark-300 mb-2">
                      Industry
                    </label>
                    <select
                      value={companyInput.industry}
                      onChange={(e) =>
                        setCompanyInput({
                          ...companyInput,
                          industry: e.target.value
                        })
                      }
                      className="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                    >
                      <option>SaaS</option>
                      <option>E-commerce</option>
                      <option>Finance</option>
                      <option>Healthcare</option>
                      <option>Education</option>
                      <option>Other</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-dark-300 mb-2">
                      Target Audience
                    </label>
                    <input
                      type="text"
                      value={companyInput.target_audience}
                      onChange={(e) =>
                        setCompanyInput({
                          ...companyInput,
                          target_audience: e.target.value
                        })
                      }
                      className="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                      placeholder="Who are you serving?"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-2">
                    Design Keywords
                  </label>
                  <div className="flex flex-wrap gap-2 mb-3">
                    {companyInput.keywords.map((k) => (
                      <span
                        key={k}
                        className="px-3 py-1 bg-primary-500/20 text-primary-300 rounded-full text-sm flex items-center gap-1"
                      >
                        {k}
                        <button
                          onClick={() => removeKeyword(k)}
                          className="hover:text-white"
                        >
                          ×
                        </button>
                      </span>
                    ))}
                  </div>
                  <input
                    type="text"
                    placeholder="Add a keyword (press Enter)"
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        const keyword = e.currentTarget.value.trim();
                        if (keyword) {
                          addKeyword(keyword);
                          e.currentTarget.value = '';
                        }
                      }
                    }}
                    className="w-full px-4 py-3 bg-dark-900/50 border border-dark-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
                  />
                </div>

                <div className="flex justify-end pt-4">
                  <button
                    onClick={handleGenerateBrief}
                    disabled={loading || !companyInput.company_name}
                    className={cn(
                      'px-8 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-all flex items-center gap-2',
                      loading || !companyInput.company_name
                        ? 'opacity-50 cursor-not-allowed'
                        : 'shadow-lg shadow-primary-500/25'
                    )}
                  >
                    {loading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <Sparkles className="w-5 h-5" />
                    )}
                    Generate Brief
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Step 2: Brief */}
        {step === 'brief' && brief && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-4xl mx-auto"
          >
            <div className="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700/50">
              <h2 className="text-2xl font-display font-bold mb-6">
                Review Your Creative Brief
              </h2>

              <div className="space-y-6">
                <div className="prose prose-invert max-w-none">
                  <h3 className="text-lg font-semibold text-primary-300 mb-3">
                    Brief Summary
                  </h3>
                  <p className="text-dark-300">{brief.brief}</p>
                </div>

                <div>
                  <h3 className="text-lg font-semibold text-primary-300 mb-3">
                    Name Suggestions
                  </h3>
                  <div className="space-y-3">
                    {brief.name_suggestions.map((suggestion, i) => (
                      <div
                        key={i}
                        className="p-4 bg-dark-900/50 border border-dark-600 rounded-lg hover:border-primary-500/50 transition-all"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-xl font-display font-bold text-white">
                            {suggestion.name}
                          </span>
                          <span className="text-sm text-dark-400">
                            {suggestion.rationale}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="flex justify-end pt-4">
                  <button
                    onClick={handleGenerateBrandKit}
                    disabled={loading}
                    className={cn(
                      'px-8 py-3 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-all flex items-center gap-2',
                      loading ? 'opacity-50 cursor-not-allowed' : 'shadow-lg shadow-primary-500/25'
                    )}
                  >
                    {loading ? (
                      <Loader2 className="w-5 h-5 animate-spin" />
                    ) : (
                      <ArrowRight className="w-5 h-5" />
                    )}
                    Forjar Identidad
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Step 3: Assets */}
        {step === 'assets' && brandKit && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="max-w-6xl mx-auto"
          >
            <div className="bg-dark-800/50 backdrop-blur-sm rounded-2xl p-8 border border-dark-700/50">
              <h2 className="text-2xl font-display font-bold mb-6">
                Your Brand Kit is Ready!
              </h2>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
                {/* Color Palettes */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-primary-300 flex items-center gap-2">
                    <Palette className="w-5 h-5" />
                    Color Palettes
                  </h3>
                  {brandKit.palettes.map((palette, i) => (
                    <div
                      key={i}
                      className="p-4 bg-dark-900/50 border border-dark-600 rounded-lg"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-dark-300">
                          {palette.name}
                        </span>
                        <button
                          onClick={() => copyToClipboard(palette.hex, `palette-${i}`)}
                          className="text-dark-400 hover:text-primary-400 transition-colors"
                        >
                          {copied === `palette-${i}` ? (
                            <Check className="w-4 h-4 text-green-400" />
                          ) : (
                            <Copy className="w-4 h-4" />
                          )}
                        </button>
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <div
                          className="w-8 h-8 rounded-full border border-dark-600"
                          style={{ backgroundColor: palette.hex }}
                        />
                        <span className="font-mono text-sm text-dark-300">
                          {palette.hex}
                        </span>
                      </div>
                      <p className="text-xs text-dark-400">{palette.desc}</p>
                    </div>
                  ))}
                </div>

                {/* Typography */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-primary-300 flex items-center gap-2">
                    <Type className="w-5 h-5" />
                    Typography
                  </h3>
                  {brandKit.typography.map((font, i) => (
                    <div
                      key={i}
                      className="p-4 bg-dark-900/50 border border-dark-600 rounded-lg"
                    >
                      <div className="flex items-center justify-between mb-2">
                        <span className="text-sm font-medium text-dark-300">
                          {font.type}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 mb-2">
                        <div className="w-16 h-6 bg-dark-800 rounded flex items-center justify-center">
                          <span className="text-white font-display font-bold">
                            {font.name}
                          </span>
                        </div>
                      </div>
                      <p className="text-xs text-dark-400">{font.desc}</p>
                    </div>
                  ))}
                </div>

                {/* Taglines */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-primary-300 flex items-center gap-2">
                    <SparklesIcon className="w-5 h-5" />
                    Taglines
                  </h3>
                  <div className="p-4 bg-dark-900/50 border border-dark-600 rounded-lg">
                    <div className="space-y-2">
                      <div>
                        <span className="text-xs text-dark-400">English</span>
                        <p className="text-lg font-display font-bold text-white">
                          {brandKit.taglines.en}
                        </p>
                      </div>
                      <div>
                        <span className="text-xs text-dark-400">Spanish</span>
                        <p className="text-lg font-display font-bold text-white">
                          {brandKit.taglines.es}
                        </p>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Logo */}
                <div className="space-y-4">
                  <h3 className="text-lg font-semibold text-primary-300 flex items-center gap-2">
                    <ImageIcon className="w-5 h-5" />
                    Logo
                  </h3>
                  <div className="p-4 bg-dark-900/50 border border-dark-600 rounded-lg">
                    <div className="flex items-center justify-center p-6 bg-dark-800 rounded-lg">
                      {brandKit.logos[0] ? (
                        <img
                          src={brandKit.logos[0]}
                          alt="Brand Logo"
                          className="max-w-full max-h-48 object-contain"
                        />
                      ) : (
                        <div className="text-dark-400 text-sm">
                          Logo generation in progress...
                        </div>
                      )}
                    </div>
                    <button
                      onClick={() => {
                        if (brandKit.logos[0]) {
                          const link = document.createElement('a');
                          link.href = brandKit.logos[0];
                          link.download = 'brand-logo.png';
                          link.click();
                        }
                      }}
                      className="w-full px-4 py-2 bg-primary-500 hover:bg-primary-600 text-white rounded-lg font-medium transition-all flex items-center justify-center gap-2"
                    >
                      <ImageIcon className="w-4 h-4" />
                      Download Logo
                    </button>
                  </div>
                </div>
              </div>

              <div className="flex justify-between items-center pt-8 border-t border-dark-700/50">
                <button
                  onClick={() => setStep('brief')}
                  className="px-6 py-2 text-dark-400 hover:text-white transition-colors"
                >
                  Edit Brief
                </button>
                <div className="text-sm text-dark-400">
                  Generated: {new Date(brandKit.generated_at).toLocaleString()}
                </div>
              </div>
            </div>
          </motion.div>
        )}

        {/* Error Display */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="max-w-4xl mx-auto"
          >
            <div className="p-4 bg-red-500/10 border border-red-500/50 rounded-lg text-red-300">
              {error}
            </div>
          </motion.div>
        )}
      </div>
    </div>
  );
}
