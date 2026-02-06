import { Code, Package, Clipboard, TrendingUp, Briefcase, Megaphone, LucideIcon } from "lucide-react";

export type DepartmentId = "engineering" | "delivery" | "admin" | "sales" | "clevel" | "marketing";

export interface Department {
  id: DepartmentId;
  name: string;
  icon: LucideIcon;
  colorClass: string;
  bgClass: string;
  borderClass: string;
}

export interface DepartmentMeta {
  id: DepartmentId;
  name: string;
  description: string;
}

export const departments: Record<DepartmentId, Department> = {
  engineering: {
    id: "engineering",
    name: "Engineering",
    icon: Code,
    colorClass: "text-department-engineering",
    bgClass: "bg-department-engineering-light",
    borderClass: "border-l-department-engineering",
  },
  delivery: {
    id: "delivery",
    name: "Delivery",
    icon: Package,
    colorClass: "text-department-delivery",
    bgClass: "bg-department-delivery-light",
    borderClass: "border-l-department-delivery",
  },
  admin: {
    id: "admin",
    name: "Admin",
    icon: Clipboard,
    colorClass: "text-department-admin",
    bgClass: "bg-department-admin-light",
    borderClass: "border-l-department-admin",
  },
  sales: {
    id: "sales",
    name: "Sales",
    icon: TrendingUp,
    colorClass: "text-department-sales",
    bgClass: "bg-department-sales-light",
    borderClass: "border-l-department-sales",
  },
  clevel: {
    id: "clevel",
    name: "C-Level",
    icon: Briefcase,
    colorClass: "text-department-clevel",
    bgClass: "bg-department-clevel-light",
    borderClass: "border-l-department-clevel",
  },
  marketing: {
    id: "marketing",
    name: "Marketing",
    icon: Megaphone,
    colorClass: "text-department-marketing",
    bgClass: "bg-department-marketing-light",
    borderClass: "border-l-department-marketing",
  },
};

export const departmentList = Object.values(departments);

export function departmentIdFromName(name: string): DepartmentId | null {
  const normalized = name.toLowerCase().replace(/[^a-z]/g, "");
  switch (normalized) {
    case "engineering":
      return "engineering";
    case "delivery":
      return "delivery";
    case "admin":
      return "admin";
    case "sales":
      return "sales";
    case "clevel":
      return "clevel";
    case "marketing":
      return "marketing";
    default:
      return null;
  }
}

export interface ChatMessage {
  id: string;
  content: string;
  sender: "user" | "department";
  department?: DepartmentId;
  timestamp: Date;
}

export interface ChatConversation {
  id: string;
  title: string;
  department: DepartmentId;
  lastMessage: string;
  timestamp: Date;
  messages: ChatMessage[];
}

export const mockResponses: Record<DepartmentId, string[]> = {
  engineering: [
    "To request API access, please submit a ticket through our internal DevPortal. You'll need your project ID and a brief description of your use case. Approval typically takes 24-48 hours.",
    "Great question! Our CI/CD pipeline uses GitHub Actions with automated testing. Check out the engineering wiki for detailed documentation on deployment processes.",
    "For code review, please follow our standard PR template and tag at least two team members. We aim to complete reviews within one business day.",
  ],
  delivery: [
    "Priority orders typically ship within 24 hours and arrive in 2-3 business days. Express shipping options are available for urgent deliveries.",
    "You can track all shipments through our logistics dashboard. Each order has a unique tracking number that updates in real-time.",
    "For bulk orders over 100 units, we recommend placing them at least 2 weeks in advance to ensure inventory availability.",
  ],
  admin: [
    "To submit expense reports, use the Finance Portal under 'Expenses > New Report'. Attach all receipts and submit for manager approval. Reimbursements process within 5 business days.",
    "PTO requests should be submitted at least 2 weeks in advance through the HR system. Emergency leave follows a different process—contact HR directly.",
    "Office supplies can be ordered through the Admin Services portal. Orders placed before 2 PM ship same-day to your desk.",
  ],
  sales: [
    "Our current pricing structure includes three tiers: Starter ($29/mo), Professional ($99/mo), and Enterprise (custom). Volume discounts are available for annual commitments.",
    "The Q4 promotion offers 20% off annual plans. This applies to new customers and upgrades from existing plans. The offer expires December 31st.",
    "For enterprise deals over $50K, please loop in the solutions engineering team for custom demonstrations and technical assessments.",
  ],
  clevel: [
    "Our Q2 goals focus on three pillars: expanding market share by 15%, launching two new product features, and improving customer retention to 95%. Monthly check-ins will track progress.",
    "The board meeting is scheduled for the 15th. Please have your departmental updates ready by the 12th for the executive summary.",
    "Our strategic priority this quarter is customer-centricity. All initiatives should tie back to improving the customer experience and satisfaction scores.",
  ],
  marketing: [
    "The next product launch is scheduled for March 15th. The campaign kicks off one week prior with teaser content across all channels. Full marketing calendar is in the shared drive.",
    "Brand guidelines have been updated—please review the new color palette and typography standards. All external communications should follow the 2024 brand book.",
    "For social media content approval, submit through the content management system at least 48 hours before intended posting time.",
  ],
};
