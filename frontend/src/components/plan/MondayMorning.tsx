"use client";

import { useMemo, useState, type ReactNode } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { ExternalLink, MapPin, Phone, Sparkles } from "lucide-react";
import { Card, CardContent } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { generateNarrative } from "@/lib/api";
import type { JobMatch, ReEntryPlan, UserProfile } from "@/lib/types";
import { CAREER_CENTER, mapsUrl, safeHref } from "@/lib/constants";

interface JobLink {
  title: string;
  company: string | null;
  url: string | null;
}

interface ActionStep {
  title: string;
  location?: string;
  phone?: string;
  url?: string;
  jobs?: JobLink[];
}

function getNextActionableDay(): string {
  const day = new Date().getDay();
  return day === 5 || day === 6 ? "Monday morning" : "tomorrow morning";
}

function collectJobs(plan: ReEntryPlan): JobLink[] {
  // Prefer bucketed arrays; fall back to job_matches only if buckets are empty
  const hasBuckets = (plan.strong_matches?.length ?? 0) + (plan.possible_matches?.length ?? 0) > 0;
  const source: JobMatch[] = hasBuckets
    ? [...(plan.strong_matches ?? []), ...(plan.possible_matches ?? [])]
    : plan.job_matches.filter((j) => j.eligible_now);
  const seen = new Set<string>();
  const jobs: JobLink[] = [];
  for (const j of source) {
    const key = `${j.title}|${j.company}`;
    if (seen.has(key)) continue;
    seen.add(key);
    jobs.push({ title: j.title, company: j.company, url: j.url });
    if (jobs.length >= 5) break;
  }
  return jobs;
}

function buildSteps(plan: ReEntryPlan): ActionStep[] {
  const steps: ActionStep[] = [];

  for (const step of plan.immediate_next_steps) {
    if (step.includes(CAREER_CENTER.name)) {
      steps.push({
        title: CAREER_CENTER.name,
        phone: CAREER_CENTER.phone,
        location: CAREER_CENTER.address,
      });
    } else {
      steps.push({ title: step });
    }
  }

  const firstBarrier = plan.barriers[0];
  if (firstBarrier?.resources[0]) {
    const resource = firstBarrier.resources[0];
    steps.push({
      title: `Visit ${resource.name}`,
      location: resource.address ?? undefined,
      phone: resource.phone ?? undefined,
      url: resource.url ?? undefined,
    });
  }

  const jobs = collectJobs(plan);
  if (jobs.length > 0) {
    steps.push({
      title: `${jobs.length} matched position${jobs.length > 1 ? "s" : ""}`,
      jobs,
    });
  }

  return steps.slice(0, 5);
}

interface MondayMorningProps {
  plan: ReEntryPlan;
  profile: UserProfile;
  firstStepAction?: ReactNode;
  sessionId?: string;
  token?: string;
}

export function MondayMorning({ plan, profile, firstStepAction, sessionId, token }: MondayMorningProps) {
  const steps = useMemo(() => buildSteps(plan), [plan]);
  const queryClient = useQueryClient();
  const [isGenerating, setIsGenerating] = useState(false);

  const generateNarrativeMutation = useMutation({
    mutationFn: () => {
      if (!sessionId || !token) throw new Error("Session ID and token required");
      return generateNarrative(sessionId, token);
    },
    onSuccess: (data) => {
      // Update the plan data in the cache with the new resident_summary
      queryClient.setQueryData(["plan", sessionId, token], (old: any) => {
        if (!old) return old;
        return {
          ...old,
          plan: {
            ...old.plan,
            resident_summary: data.summary,
          },
        };
      });
    },
    onError: (error) => {
      console.error("Failed to generate narrative:", error);
    },
    onSettled: () => {
      setIsGenerating(false);
    },
  });

  const handleGenerateNarrative = () => {
    if (!sessionId || !token) return;
    setIsGenerating(true);
    generateNarrativeMutation.mutate();
  };

  return (
    <section className="space-y-8">
      <div className="space-y-3">
        <h1 className="text-3xl sm:text-4xl font-bold text-primary tracking-tight">
          Here&apos;s what you can do {getNextActionableDay()}.
        </h1>
        <p className="text-lg text-muted-foreground">
          Your personalized action plan for Montgomery, AL
          {profile.barrier_count > 0 && (
            <>, addressing {profile.barrier_count} barrier{profile.barrier_count > 1 ? "s" : ""}</>
          )}
        </p>
      </div>

      {/* AI-generated narrative */}
      {plan.resident_summary ? (
        <Card className="border-primary/20 bg-primary/5">
          <CardContent className="p-6">
            <div className="space-y-3">
              <h2 className="text-lg font-semibold text-primary">Your Personalized Plan Summary</h2>
              <p className="text-sm leading-relaxed text-foreground">
                {plan.resident_summary}
              </p>
            </div>
          </CardContent>
        </Card>
      ) : (
        <Card className="border-dashed border-muted-foreground/30">
          <CardContent className="p-6">
            <div className="space-y-4">
              <div className="space-y-2">
                <h2 className="text-lg font-semibold text-foreground">Generate Your Personalized Summary</h2>
                <p className="text-sm text-muted-foreground">
                  Get an AI-powered narrative that explains your plan in a warm, encouraging way.
                </p>
              </div>
              <Button 
                onClick={handleGenerateNarrative}
                disabled={isGenerating || !sessionId || !token}
                className="w-full sm:w-auto"
              >
                <Sparkles className="h-4 w-4 mr-2" />
                {isGenerating ? "Generating..." : "Generate Summary"}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      <div>
        <h2 className="text-xl font-semibold text-primary mb-4">Your Next Steps</h2>
        <div className="flex flex-wrap justify-center gap-3">
          {steps.map((step, i) => (
            <Card key={i} className="group flex flex-col w-full sm:w-[calc(50%-0.375rem)] lg:w-[calc(33.333%-0.5rem)]">
              <CardContent className="p-4 flex flex-col gap-2 flex-1">
                <div className="flex items-start gap-2">
                  <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-secondary text-secondary-foreground text-xs font-bold mt-0.5">
                    {i + 1}
                  </span>
                  <h3 className="text-sm font-semibold text-foreground leading-snug">{step.title}</h3>
                </div>

                {/* Details revealed on hover */}
                <div className="block sm:max-h-0 sm:overflow-hidden sm:group-hover:max-h-96 sm:group-focus-within:max-h-96 transition-all duration-200 text-xs space-y-1.5 ml-8">
                  {step.phone && (
                    <a href={`tel:${step.phone}`} className="flex items-center gap-1 text-secondary hover:underline">
                      <Phone className="h-3 w-3" />
                      {step.phone}
                    </a>
                  )}
                  {step.location && (
                    <a
                      href={mapsUrl(step.location)}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-1 text-secondary hover:underline"
                    >
                      <MapPin className="h-3 w-3" />
                      {step.location}
                    </a>
                  )}
                  {step.url && safeHref(step.url) && (
                    <a href={safeHref(step.url)} target="_blank" rel="noopener noreferrer" className="flex items-center gap-1 text-secondary hover:underline">
                      <ExternalLink className="h-3 w-3" />
                      Website
                    </a>
                  )}
                  {step.jobs && step.jobs.length > 0 && (
                    <ul className="space-y-1">
                      {step.jobs.map((job, j) => (
                        <li key={j}>
                          <a
                            href="#matched-jobs"
                            className="text-secondary hover:underline"
                          >
                            {job.title}{job.company ? ` at ${job.company}` : ""}
                          </a>
                        </li>
                      ))}
                    </ul>
                  )}
                </div>

                {i === 0 && firstStepAction && (
                  <div className="mt-auto pt-2 flex justify-center">
                    {firstStepAction}
                  </div>
                )}
              </CardContent>
            </Card>
          ))}
        </div>
      </div>
    </section>
  );
}
