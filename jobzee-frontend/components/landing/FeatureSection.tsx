"use client";

import React from "react";
import { motion } from "framer-motion";
import {
  Brain,
  Target,
  Zap,
  Shield,
  BarChart3,
  MessageSquare,
  Search,
  UserCheck,
  TrendingUp,
  Clock,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Matching",
    description:
      "Advanced algorithms analyze your skills, experience, and preferences to find the perfect job match.",
    color: "bg-blue-100 text-blue-600",
  },
  {
    icon: Target,
    title: "Precision Targeting",
    description:
      "Get matched with opportunities that align with your career goals and personal preferences.",
    color: "bg-green-100 text-green-600",
  },
  {
    icon: Zap,
    title: "Instant Results",
    description:
      "Receive job recommendations in seconds, not days. Our AI works 24/7 to find your next opportunity.",
    color: "bg-yellow-100 text-yellow-600",
  },
  {
    icon: Shield,
    title: "Secure & Private",
    description:
      "Your data is protected with enterprise-grade security. We never share your information without consent.",
    color: "bg-purple-100 text-purple-600",
  },
  {
    icon: BarChart3,
    title: "Smart Analytics",
    description:
      "Track your application progress and get insights into your job search performance.",
    color: "bg-indigo-100 text-indigo-600",
  },
  {
    icon: MessageSquare,
    title: "Direct Communication",
    description:
      "Connect directly with employers through our integrated messaging system.",
    color: "bg-pink-100 text-pink-600",
  },
];

const stats = [
  { icon: Search, label: "Jobs Analyzed", value: "50K+" },
  { icon: UserCheck, label: "Successful Matches", value: "15K+" },
  { icon: TrendingUp, label: "Success Rate", value: "95%" },
  { icon: Clock, label: "Avg. Response Time", value: "< 24h" },
];

export const FeatureSection: React.FC = () => {
  return (
    <section className="py-20 bg-white">
      <div className="container mx-auto px-4 sm:px-6 lg:px-8">
        {/* Section Header */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="text-3xl sm:text-4xl font-bold text-gray-900 mb-4">
            Why Choose JobZee?
          </h2>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Our AI-powered platform revolutionizes the job search experience,
            making it faster, smarter, and more effective than traditional
            methods.
          </p>
        </motion.div>

        {/* Features Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 mb-20">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              viewport={{ once: true }}
              className="group p-6 rounded-xl border border-gray-200 hover:border-blue-300 hover:shadow-lg transition-all duration-300"
            >
              <div
                className={`w-12 h-12 ${feature.color} rounded-lg flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
              >
                <feature.icon className="w-6 h-6" />
              </div>
              <h3 className="text-xl font-semibold text-gray-900 mb-3">
                {feature.title}
              </h3>
              <p className="text-gray-600 leading-relaxed">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </div>

        {/* Stats Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          viewport={{ once: true }}
          className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-2xl p-8 lg:p-12"
        >
          <div className="text-center mb-12">
            <h3 className="text-2xl sm:text-3xl font-bold text-gray-900 mb-4">
              Trusted by Thousands
            </h3>
            <p className="text-gray-600">
              Join our growing community of successful job seekers and employers
            </p>
          </div>

          <div className="grid grid-cols-2 lg:grid-cols-4 gap-8">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.8 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.6, delay: index * 0.1 }}
                viewport={{ once: true }}
                className="text-center"
              >
                <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center mx-auto mb-4 shadow-lg">
                  <stat.icon className="w-8 h-8 text-blue-600" />
                </div>
                <div className="text-3xl font-bold text-gray-900 mb-2">
                  {stat.value}
                </div>
                <div className="text-gray-600 text-sm">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
};
