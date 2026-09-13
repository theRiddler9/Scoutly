import { useState, useEffect } from 'react';
import { User, GitBranch, Mail, Code, Briefcase, Plus, X, Save, CheckCircle, Globe, AtSign, RefreshCcw } from 'lucide-react';
import { profileApi, opportunitiesApi } from '../services/api';

export default function Profile() {
  const emptyProfile = {
    name: '',
    email: '',
    github_url: '',
    skills: [],
    projects: [],
    resume_text: '',
    social_handles: { twitter: '', linkedin: '', website: '' },
  };

  const [profile, setProfile] = useState(emptyProfile);
  const [newSkill, setNewSkill] = useState('');
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(false);
  const [isNew, setIsNew] = useState(false);

  useEffect(() => {
    loadProfile();
  }, []);

  const loadProfile = async () => {
    try {
      const res = await profileApi.get(1);
      setProfile(res.data);
    } catch (err) {
      if (err.response?.status === 404) {
        setIsNew(true);
      }
    } finally {
      setLoading(false);
    }
  };

  const saveProfile = async (profileToSave = profile) => {
    setSaving(true);
    try {
      if (isNew) {
        await profileApi.create(profileToSave);
        setIsNew(false);
      } else {
        await profileApi.update(1, profileToSave);
      }
      // Re-trigger matching so opportunities update with new profile
      await opportunitiesApi.triggerMatch({ profile_id: 1 });
      
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (err) {
      console.error('Save failed:', err);
    } finally {
      setSaving(false);
    }
  };

  const clearProfile = async () => {
    if (confirm('Are you sure you want to clear your profile? This will reset all your details.')) {
      setProfile(emptyProfile);
      await saveProfile(emptyProfile);
    }
  };

  const addSkill = () => {
    if (newSkill.trim() && !profile.skills.includes(newSkill.trim())) {
      setProfile(p => ({ ...p, skills: [...p.skills, newSkill.trim()] }));
      setNewSkill('');
    }
  };

  const removeSkill = (skill) => {
    setProfile(p => ({ ...p, skills: p.skills.filter(s => s !== skill) }));
  };

  const addProject = () => {
    setProfile(p => ({
      ...p,
      projects: [...p.projects, { title: '', description: '', tech_stack: '' }],
    }));
  };

  const updateProject = (index, field, value) => {
    setProfile(p => {
      const updated = [...p.projects];
      updated[index] = { ...updated[index], [field]: value };
      return { ...p, projects: updated };
    });
  };

  const removeProject = (index) => {
    setProfile(p => ({
      ...p,
      projects: p.projects.filter((_, i) => i !== index),
    }));
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="glass-card p-8">
          <div className="skeleton h-8 w-48 mb-6" />
          <div className="space-y-4">
            {[1, 2, 3, 4].map(i => <div key={i} className="skeleton h-12 w-full" />)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between mb-8 gap-4">
        <div>
          <h1 className="text-2xl sm:text-3xl font-bold">
            <span className="gradient-text">Your Profile</span>
          </h1>
          <p className="text-gray-400 mt-1 text-sm">
            This info powers AI matching & auto-fill
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={clearProfile}
            className="btn-danger"
          >
            <RefreshCcw className="w-4 h-4" /> Clear Profile
          </button>
          <button
            onClick={() => saveProfile(profile)}
            disabled={saving}
            className={saved ? 'btn-success' : 'btn-primary'}
          >
            {saved ? (
              <>
                <CheckCircle className="w-4 h-4" /> Saved!
              </>
            ) : saving ? (
              'Saving & Matching...'
            ) : (
              <>
                <Save className="w-4 h-4" /> Save Profile
              </>
            )}
          </button>
        </div>
      </div>

      <div className="space-y-6">
        {/* Basic Info */}
        <div className="glass-card p-6 animate-slide-up">
          <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            <User className="w-5 h-5 text-primary-400" />
            Basic Information
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div>
              <label className="input-label">Full Name <span className="text-red-400">*</span></label>
              <input
                type="text"
                className="input-field"
                placeholder="Your full name"
                value={profile.name}
                onChange={e => setProfile(p => ({ ...p, name: e.target.value }))}
              />
            </div>
            <div>
              <label className="input-label flex items-center gap-2">
                <Mail className="w-3.5 h-3.5" /> Email <span className="text-red-400">*</span>
              </label>
              <input
                type="email"
                className="input-field"
                placeholder="you@example.com"
                value={profile.email}
                onChange={e => setProfile(p => ({ ...p, email: e.target.value }))}
              />
            </div>
            <div>
              <label className="input-label flex items-center gap-2">
                <GitBranch className="w-3.5 h-3.5" /> GitHub URL
              </label>
              <input
                type="url"
                className="input-field"
                placeholder="https://github.com/username"
                value={profile.github_url}
                onChange={e => setProfile(p => ({ ...p, github_url: e.target.value }))}
              />
            </div>
          </div>
        </div>

        {/* Social Handles */}
        <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '0.1s' }}>
          <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            <Globe className="w-5 h-5 text-primary-400" />
            Social Profiles
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="input-label flex items-center gap-2">
                <AtSign className="w-3.5 h-3.5" /> Twitter / X
              </label>
              <input
                type="text"
                className="input-field"
                placeholder="@username"
                value={profile.social_handles?.twitter || ''}
                onChange={e => setProfile(p => ({
                  ...p,
                  social_handles: { ...p.social_handles, twitter: e.target.value },
                }))}
              />
            </div>
            <div>
              <label className="input-label">LinkedIn</label>
              <input
                type="url"
                className="input-field"
                placeholder="https://linkedin.com/in/..."
                value={profile.social_handles?.linkedin || ''}
                onChange={e => setProfile(p => ({
                  ...p,
                  social_handles: { ...p.social_handles, linkedin: e.target.value },
                }))}
              />
            </div>
            <div>
              <label className="input-label">Website</label>
              <input
                type="url"
                className="input-field"
                placeholder="https://yoursite.com"
                value={profile.social_handles?.website || ''}
                onChange={e => setProfile(p => ({
                  ...p,
                  social_handles: { ...p.social_handles, website: e.target.value },
                }))}
              />
            </div>
          </div>
        </div>

        {/* Skills */}
        <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '0.2s' }}>
          <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            <Code className="w-5 h-5 text-primary-400" />
            Skills & Technologies
          </h2>
          <div className="flex gap-3 mb-6">
            <input
              type="text"
              className="input-field flex-1"
              placeholder="Add a skill (e.g., Python, React, ML)"
              value={newSkill}
              onChange={e => setNewSkill(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && addSkill()}
            />
            <button onClick={addSkill} className="btn-secondary">
              <Plus className="w-4 h-4" /> Add
            </button>
          </div>
          <div className="flex flex-wrap gap-3">
            {profile.skills.map((skill, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-semibold transition-all duration-200 group cursor-pointer"
                style={{
                  background: 'rgba(76, 110, 245, 0.15)',
                  border: '1px solid rgba(76, 110, 245, 0.3)',
                  color: '#bac8ff',
                }}
                onClick={() => removeSkill(skill)}
              >
                {skill}
                <X className="w-5 h-5 text-red-400 hover:text-red-300" />
              </span>
            ))}
            {profile.skills.length === 0 && (
              <p className="text-gray-500 text-sm">No skills added yet</p>
            )}
          </div>
        </div>

        {/* Projects */}
        <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '0.3s' }}>
          <div className="flex items-center justify-between mb-5">
            <h2 className="text-lg font-semibold text-white flex items-center gap-2">
              <Briefcase className="w-5 h-5 text-primary-400" />
              Projects
            </h2>
            <button onClick={addProject} className="btn-secondary text-sm">
              <Plus className="w-4 h-4" /> Add Project
            </button>
          </div>
          <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
            {profile.projects.map((project, i) => (
              <div
                key={i}
                className="p-5 rounded-2xl relative"
                style={{
                  background: 'rgba(255, 255, 255, 0.03)',
                  border: '1px solid rgba(255, 255, 255, 0.08)',
                }}
              >
                <button
                  onClick={() => removeProject(i)}
                  className="absolute top-4 right-4 p-2 rounded-xl bg-red-500/10 hover:bg-red-500/20 transition-all border border-red-500/20"
                >
                  <X className="w-5 h-5 text-red-400" />
                </button>
                <div className="grid grid-cols-1 gap-4 pr-12">
                  <div>
                    <label className="input-label">Project Title</label>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="My Awesome Project"
                      value={project.title}
                      onChange={e => updateProject(i, 'title', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="input-label">Tech Stack</label>
                    <input
                      type="text"
                      className="input-field"
                      placeholder="React, Python, TensorFlow"
                      value={project.tech_stack}
                      onChange={e => updateProject(i, 'tech_stack', e.target.value)}
                    />
                  </div>
                  <div>
                    <label className="input-label">Description</label>
                    <textarea
                      className="input-field"
                      rows={3}
                      placeholder="Describe what this project does..."
                      value={project.description}
                      onChange={e => updateProject(i, 'description', e.target.value)}
                    />
                  </div>
                </div>
              </div>
            ))}
          </div>
            {profile.projects.length === 0 && (
              <p className="text-gray-500 text-sm text-center py-4">
                No projects added yet. Add 2-3 projects for better matching.
              </p>
            )}
        </div>

        {/* Resume */}
        <div className="glass-card p-6 animate-slide-up" style={{ animationDelay: '0.4s' }}>
          <h2 className="text-lg font-semibold text-white mb-5 flex items-center gap-2">
            📄 Resume / Bio
          </h2>
          <textarea
            className="input-field"
            rows={8}
            placeholder="Paste your resume text, bio, or a brief summary of your experience..."
            value={profile.resume_text}
            onChange={e => setProfile(p => ({ ...p, resume_text: e.target.value }))}
          />
        </div>
      </div>
    </div>
  );
}
