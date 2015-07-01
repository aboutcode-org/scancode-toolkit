package clime.messadmin.admin;

import java.io.IOException;
import java.util.ArrayList;
import java.util.Collection;
import java.util.Collections;
import java.util.Comparator;
import java.util.Date;
import java.util.List;
import java.util.Locale;

import javax.servlet.Servlet;
import javax.servlet.ServletException;
import javax.servlet.http.HttpServlet;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;
import javax.servlet.http.HttpSession;

import clime.messadmin.core.Constants;
import clime.messadmin.core.MessAdmin;
import clime.messadmin.model.Application;
import clime.messadmin.model.IApplicationInfo;
import clime.messadmin.model.IServerInfo;
import clime.messadmin.model.Server;
import clime.messadmin.model.Session;
import clime.messadmin.utils.ComparableBoolean;
import clime.messadmin.utils.ReverseComparator;
import clime.messadmin.utils.SessionUtils;

import com.indus.utils.encryption.EncryptionUtil;

/**
 * Servlet implementation class for Servlet: MessAdminServlet
 * Injects a message into every active sessions
 * IMPLEMENTATION NOTE: always use include() instead of forward(), to get the real name of this servlet in jsp's
 * @author C&eacute;drik LIME
 */
 public class MessAdminServlet extends HttpServlet implements Servlet {
	private static final boolean DEBUG = false;

    private static final String METHOD_POST = "POST";

	protected String webFilesRoot = "/MessAdmin/";//$NON-NLS-1$
	protected String serverInfosJspPath = webFilesRoot + "serverInfos.jsp";//$NON-NLS-1$
	protected String webAppsListJspPath = webFilesRoot + "webAppsList.jsp";//$NON-NLS-1$
	protected String webAppStatsJspPath = webFilesRoot + "webAppStats.jsp";//$NON-NLS-1$
	protected String sessionsListJspPath = webFilesRoot + "sessionsList.jsp";//$NON-NLS-1$
	protected String sessionDetailJspPath = webFilesRoot + "sessionDetail.jsp";//$NON-NLS-1$

	protected String authorizationPassword = null;

	/** {@inheritDoc} */
	public void log(String message) {
		if (DEBUG) {
			getServletContext().log(getServletName() + ": " + message);
		}
	}

	/** {@inheritDoc} */
	public void log(String message, Throwable t) {
		if (DEBUG) {
			getServletContext().log(getServletName() + ": " + message, t);
		}
	}

	/* (non-Java-doc)
	 * @see javax.servlet.http.HttpServlet#HttpServlet()
	 */
	public MessAdminServlet() {
		super();
	}

	/**
	 * {@inheritDoc}
	 */
	protected void doGet(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		process(req, resp);
	}

	/**
	 * {@inheritDoc}
	 */
	protected void doPost(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		process(req, resp);
	}

	/**
	 * Dispatcher method which processes the request
	 * @param req
	 * @param resp
	 * @throws ServletException
	 * @throws IOException
	 */
	protected void process(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		// Some attributes needed by some or all JSPs
		req.setAttribute("autorefresh", req.getParameter("autorefresh"));//$NON-NLS-1$ //$NON-NLS-2$
		req.setAttribute("WebFilesRoot", req.getContextPath() + webFilesRoot);//$NON-NLS-1$
		if (req.getParameter(Constants.APPLICATION_MESSAGE) != null) {
			req.setAttribute(Constants.APPLICATION_MESSAGE, req.getParameter(Constants.APPLICATION_MESSAGE));
		}
		if (req.getParameter(Constants.APPLICATION_ERROR) != null) {
			req.setAttribute(Constants.APPLICATION_ERROR, req.getParameter(Constants.APPLICATION_ERROR));
		}

		resp.setContentType("text/html");//should be "application/xhtml+xml", but IE screws us once again...
		resp.setLocale(Locale.ENGLISH);

		if (! HTTPAuthorizationProvider.checkAccess(authorizationPassword, req, resp)) {
			return;
		}

		String action = req.getParameter("action");//$NON-NLS-1$
		// The Big Dispatch(TM), part 1
		if ("serverInfos".equals(action)) {//$NON-NLS-1$
			displayServerInfosPage(req, resp);
			return;
		} else if ("webAppsList".equals(action)) {//$NON-NLS-1$
			displayWebAppsList(req, resp);
			return;
		} else if ("injectApplications".equals(action)) {//$NON-NLS-1$
			String permanent =  req.getParameter("permanent");
			String[] applicationIds = req.getParameterValues("applicationIds");//$NON-NLS-1$
			String message = req.getParameter("message");//$NON-NLS-1$
			int i;
			if (permanent != null) {
				i = MessAdmin.injectApplicationsPermanent(applicationIds, message);
			} else {
				i = MessAdmin.injectApplicationsOnce(applicationIds, message);
			}
			req.setAttribute(Constants.APPLICATION_MESSAGE, "" + i + " applications modified.");
			displayWebAppsList(req, resp);
			return;
		}

		// Get the WebApp context we want to work with
		String context = req.getParameter("context");//$NON-NLS-1$
		if (context == null && Server.getInstance().getAllKnownInternalContexts().size() == 1) {
			context = (String) Server.getInstance().getAllKnownInternalContexts().toArray()[0];//req.getContextPath();
		}
		// If no or invalid context, display a list of available WebApps
		if (context == null || Server.getInstance().getApplication(context) == null) {
			displayWebAppsList(req, resp);
			return;
		}
		req.setAttribute("context", context);//$NON-NLS-1$

		// The Big Dispatch(TM), part 2
		if ("webAppStats".equals(action)) {//$NON-NLS-1$
			displayWebAppStatsPage(req, resp, context);
			return;
		} else if ("sessionsList".equals(action)) {//$NON-NLS-1$
			displaySessionsListPage(req, resp, context);
			return;
		} else if ("sessionDetail".equals(action)) {//$NON-NLS-1$
			String sessionId = req.getParameter("sessionId");//$NON-NLS-1$
			displaySessionDetailPage(req, resp, context, sessionId);
			return;
		} else if ("removeServletContextAttribute".equals(action)) {//$NON-NLS-1$
			String name = req.getParameter("attributeName");//$NON-NLS-1$
			IApplicationInfo applicationInfo = Server.getInstance().getApplication(context).getApplicationInfo();
			boolean removed = (null != applicationInfo.getAttribute(name));
			applicationInfo.removeAttribute(name);
			String outMessage = removed ? "Context attribute '" + name + "' removed." : "Context " + context + " did not contain any attribute named '" + name + '\'';
			req.setAttribute(Constants.APPLICATION_MESSAGE, outMessage);
			resp.sendRedirect(resp.encodeRedirectURL(req.getRequestURL().append("?action=webAppStats&context=").append(context).toString()));
			return;
		} else if ("injectApplication".equals(action)) {//$NON-NLS-1$
			String message = req.getParameter("message");//$NON-NLS-1$
			Application application = Server.getInstance().getApplication(context);
			application.injectPermanentMessage(message);
			req.setAttribute(Constants.APPLICATION_MESSAGE, "Global message set.");
			displaySessionsListPage(req, resp, context);
			return;
		} else if ("injectSessions".equals(action)) {//$NON-NLS-1$
			String[] sessionIds = req.getParameterValues("sessionIds");//$NON-NLS-1$
			String message = req.getParameter("message");//$NON-NLS-1$
			int i = MessAdmin.injectSessions(context, sessionIds, message);
			req.setAttribute(Constants.APPLICATION_MESSAGE, "" + i + " sessions modified.");
			displaySessionsListPage(req, resp, context);
			return;
		} else if ("invalidateSessions".equals(action)) {//$NON-NLS-1$
			String[] sessionIds = req.getParameterValues("sessionIds");//$NON-NLS-1$
			int i = MessAdmin.invalidateSessions(context, sessionIds);
			req.setAttribute(Constants.APPLICATION_MESSAGE, "" + i + " sessions invalidated.");
			displaySessionsListPage(req, resp, context);
			return;
		} else if ("setSessionMaxInactiveInterval".equals(action)) {//$NON-NLS-1$
			String sessionId = req.getParameter("sessionId");//$NON-NLS-1$
			String timeoutStr = req.getParameter("timeout");//$NON-NLS-1$
			try {
				int timeout = Integer.parseInt(timeoutStr.trim()) * 60;
				int oldTimeout = MessAdmin.setSessionMaxInactiveInterval(context, sessionId, timeout);
				String outMessage = oldTimeout != 0 ? "Session " + sessionId + " timeout set from " + oldTimeout/60 + " minutes to " + timeoutStr + " minutes." : "Could not set Session timeout for id " + sessionId;
				req.setAttribute(Constants.APPLICATION_MESSAGE, outMessage);
			} catch (NumberFormatException nfe) {
				req.setAttribute(Constants.APPLICATION_ERROR, "Please specify a timeout in minutes!");
			} catch (NullPointerException npe) {
				req.setAttribute(Constants.APPLICATION_ERROR, "Please specify a timeout in minutes!");
			}
			resp.sendRedirect(resp.encodeRedirectURL(req.getRequestURL().append("?action=sessionDetail&context=").append(context).append("&sessionId=").append(sessionId).toString()));
			return;
		} else if ("removeSessionAttribute".equals(action)) {//$NON-NLS-1$
			String sessionId = req.getParameter("sessionId");//$NON-NLS-1$
			String name = req.getParameter("attributeName");//$NON-NLS-1$
			boolean removed = MessAdmin.removeSessionAttribute(context, sessionId, name);
			String outMessage = removed ? "Session attribute '" + name + "' removed." : "Session did not contain any attribute named '" + name + '\'';
			req.setAttribute(Constants.APPLICATION_MESSAGE, outMessage);
			resp.sendRedirect(resp.encodeRedirectURL(req.getRequestURL().append("?action=sessionDetail&context=").append(context).append("&sessionId=").append(sessionId).toString()));
			return;
		} // else
		// default fall-back action
		displaySessionsListPage(req, resp, context);
	}

	private StringBuffer getMessages(HttpServletRequest req) {
		StringBuffer buffer = new StringBuffer();
		if (req.getAttribute(Constants.APPLICATION_MESSAGE) != null) {
			buffer.append('&').append(Constants.APPLICATION_MESSAGE).append('=').append(req.getAttribute(Constants.APPLICATION_MESSAGE));
		}
		if (req.getAttribute(Constants.APPLICATION_ERROR) != null) {
			buffer.append('&').append(Constants.APPLICATION_ERROR).append('=').append(req.getAttribute(Constants.APPLICATION_ERROR));
		}
		return buffer;
	}

	/**
	 * Displays the Web Applications list
	 * @param req
	 * @param resp
	 * @throws ServletException
	 * @throws IOException
	 */
	protected void displayWebAppsList(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		if (METHOD_POST.equals(req.getMethod())) {
			resp.sendRedirect(resp.encodeRedirectURL(req.getRequestURL().append("?action=webAppsList").append(getMessages(req)).toString()));
			return;
		}
		req.setAttribute("applications", Server.getInstance().getApplicationInfos());//$NON-NLS-1$
		// <strong>NOTE</strong> - This header will be overridden
		// automatically if a <code>RequestDispatcher.forward()</code> call is
		// ultimately invoked.
		resp.setHeader("Pragma", "No-cache"); // HTTP 1.0 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setHeader("Cache-Control", "no-cache,no-store,max-age=0"); // HTTP 1.1 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setDateHeader("Expires", 0); // 0 means now //$NON-NLS-1$
		getServletContext().getRequestDispatcher(webAppsListJspPath).include(req, resp);
	}

	/**
	 * Displays the HttpSessions list for a given WebApp (context)
	 * @param req
	 * @param resp
	 * @param context internal context name for required WebApp
	 * @throws ServletException
	 * @throws IOException
	 */
	protected void displaySessionsListPage(HttpServletRequest req, HttpServletResponse resp, String context) throws ServletException, IOException {
		if (METHOD_POST.equals(req.getMethod())) {
			StringBuffer buffer = req.getRequestURL().append("?action=sessionsList&context=").append(context);
			if (req.getAttribute("sort") != null) {
				buffer.append('&').append("sort=").append(req.getAttribute("sort"));
			}
			if (req.getAttribute("order") != null) {
				buffer.append('&').append("order=").append(req.getAttribute("order"));
			}
			resp.sendRedirect(resp.encodeRedirectURL(buffer.append(getMessages(req)).toString()));
			return;
		}
		Collection activeSessions = Server.getInstance().getApplication(context).getActiveSessionInfos();
		String sortBy = req.getParameter("sort");//$NON-NLS-1$
		String orderBy = null;
		if (null != sortBy && !"".equals(sortBy.trim())) {
			activeSessions = new ArrayList(activeSessions);
			Comparator comparator = getComparator(sortBy);
			if (comparator != null) {
				orderBy = req.getParameter("order");//$NON-NLS-1$
				if ("DESC".equalsIgnoreCase(orderBy)) {//$NON-NLS-1$
					comparator = new ReverseComparator(comparator);
					//orderBy = "ASC";
				} else {
					//orderBy = "DESC";
				}
				try {
					Collections.sort((List)activeSessions, comparator);
				} catch (IllegalStateException ise) {
					// at least 1 session is invalidated
					req.setAttribute(Constants.APPLICATION_ERROR, "Can't sort session list: one session is invalidated");
				}
			} else {
				log("WARNING: unknown sort order: " + sortBy);
			}
		}
		// keep sort order
		req.setAttribute("sort", sortBy);
		req.setAttribute("order", orderBy);
		req.setAttribute("activeSessions", activeSessions);//$NON-NLS-1$
		req.setAttribute("passiveSessionsIds", Server.getInstance().getApplication(context).getPassiveSessionsIds());//$NON-NLS-1$
		req.setAttribute("webAppStats", Server.getInstance().getApplication(context).getApplicationInfo());//$NON-NLS-1$
		// <strong>NOTE</strong> - This header will be overridden
		// automatically if a <code>RequestDispatcher.forward()</code> call is
		// ultimately invoked.
		resp.setHeader("Pragma", "No-cache"); // HTTP 1.0 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setHeader("Cache-Control", "no-cache,no-store,max-age=0"); // HTTP 1.1 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setDateHeader("Expires", 0); // 0 means now //$NON-NLS-1$
		getServletContext().getRequestDispatcher(sessionsListJspPath).include(req, resp);
	}

	/**
	 * Displays the details page for a given HttpSession
	 * @param req
	 * @param resp
	 * @param context internal context name for required WebApp
	 * @throws ServletException
	 * @throws IOException
	 */
	protected void displaySessionDetailPage(HttpServletRequest req, HttpServletResponse resp, String context, String sessionId) throws ServletException, IOException {
		if (METHOD_POST.equals(req.getMethod())) {
			resp.sendRedirect(resp.encodeRedirectURL(req.getRequestURL().append("?action=sessionDetail&context=").append(context).append("&sessionId=").append(sessionId).append(getMessages(req)).toString()));
			return;
		}
		Application application = Server.getInstance().getApplication(context);
		Session session = application.getSession(sessionId);
		if (null == session) {
			String error = "WARNING: null session display requested: " + sessionId;
			log(error);
			req.setAttribute(Constants.APPLICATION_ERROR, error);
			displaySessionsListPage(req, resp, context);
			return;
		}
		// <strong>NOTE</strong> - This header will be overridden
		// automatically if a <code>RequestDispatcher.forward()</code> call is
		// ultimately invoked.
		resp.setHeader("Pragma", "No-cache"); // HTTP 1.0 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setHeader("Cache-Control", "no-cache,no-store,max-age=0"); // HTTP 1.1 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setDateHeader("Expires", 0); // 0 means now //$NON-NLS-1$
		req.setAttribute("webAppStats", application.getApplicationInfo());//$NON-NLS-1$
		req.setAttribute("currentSession", session.getSessionInfo());//$NON-NLS-1$
		req.setAttribute("currentSessionExtraInfo", session.getSessionInfo());//$NON-NLS-1$
		getServletContext().getRequestDispatcher(sessionDetailJspPath).include(req, resp);
	}

	/**
	 * Displays the details page for a Web Application
	 * @param req
	 * @param resp
	 * @param context internal context name for required WebApp
	 * @throws ServletException
	 * @throws IOException
	 */
	protected void displayWebAppStatsPage(HttpServletRequest req, HttpServletResponse resp, String context) throws ServletException, IOException {
		if (METHOD_POST.equals(req.getMethod())) {
			resp.sendRedirect(resp.encodeRedirectURL(req.getRequestURL().append("?action=webAppStats&context=").append(context).append(getMessages(req)).toString()));
			return;
		}
		IApplicationInfo webAppStats = Server.getInstance().getApplication(context).getApplicationInfo();
		// <strong>NOTE</strong> - This header will be overridden
		// automatically if a <code>RequestDispatcher.forward()</code> call is
		// ultimately invoked.
		resp.setHeader("Pragma", "No-cache"); // HTTP 1.0 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setHeader("Cache-Control", "no-cache,no-store,max-age=0"); // HTTP 1.1 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setDateHeader("Expires", 0); // 0 means now //$NON-NLS-1$
		req.setAttribute("webAppStats", webAppStats);//$NON-NLS-1$
		getServletContext().getRequestDispatcher(webAppStatsJspPath).include(req, resp);
	}

	/**
	 * Displays the page for the Server Informations
	 * @param req
	 * @param resp
	 * @throws ServletException
	 * @throws IOException
	 */
	protected void displayServerInfosPage(HttpServletRequest req, HttpServletResponse resp) throws ServletException, IOException {
		if (METHOD_POST.equals(req.getMethod())) {
			resp.sendRedirect(resp.encodeRedirectURL(req.getRequestURL().append("?action=serverInfos").append(getMessages(req)).toString()));
			return;
		}
		IServerInfo serverInfo = Server.getInstance().getServerInfo();
		// <strong>NOTE</strong> - This header will be overridden
		// automatically if a <code>RequestDispatcher.forward()</code> call is
		// ultimately invoked.
		resp.setHeader("Pragma", "No-cache"); // HTTP 1.0 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setHeader("Cache-Control", "no-cache,no-store,max-age=0"); // HTTP 1.1 //$NON-NLS-1$ //$NON-NLS-2$
		resp.setDateHeader("Expires", 0); // 0 means now //$NON-NLS-1$
		req.setAttribute("serverInfos", serverInfo);//$NON-NLS-1$
		getServletContext().getRequestDispatcher(serverInfosJspPath).include(req, resp);
	}


	/**
	 * Comparator used on the HttpSessions list, when sorting is required
	 * @param sortBy
	 * @return Comparator
	 */
	protected Comparator getComparator(String sortBy) {
		Comparator comparator = null;
		if ("CreationTime".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					return new Date(session.getCreationTime());
				}
			};
		} else if ("id".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					return session.getId();
				}
			};
		} else if ("LastAccessedTime".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					return new Date(session.getLastAccessedTime());
				}
			};
		} else if ("MaxInactiveInterval".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					return new Date(session.getMaxInactiveInterval());
				}
			};
		} else if ("new".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					return ComparableBoolean.valueOf(session.isNew());
				}
			};
		} else if ("locale".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					Locale locale = SessionUtils.guessLocaleFromSession(session);
					return (null == locale) ? "" : locale.toString();
				}
			};
		} else if ("user".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					Object user = SessionUtils.guessUserFromSession(session);
					return (null == user) ? "" : user.toString();
				}
			};
		} else if ("UsedTime".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					return new Date(SessionUtils.getUsedTimeForSession(session));
				}
			};
		} else if ("IdleTime".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					return new Date(SessionUtils.getIdleTimeForSession(session));
				}
			};
		} else if ("TTL".equalsIgnoreCase(sortBy)) {//$NON-NLS-1$
			comparator = new BaseSessionComparator() {
				public Comparable getComparableObject(HttpSession session) {
					return new Date(SessionUtils.getTTLForSession(session));
				}
			};
		}
		//TODO: complete this to TTL, etc.
		return comparator;
	}



	/**
	 * {@inheritDoc}
	 */
	public String getServletInfo() {
		return "MessAdminServlet, copyright (c) 2005-2006 Cédrik LIME";
	}

	/**
	 * {@inheritDoc}
	 */
	public void init() throws ServletException {
		super.init();
		String initAuthorizationPassword = getServletConfig().getInitParameter("AuthorizationPassword");//$NON-NLS-1$
		if (null != initAuthorizationPassword) {
            try {
                authorizationPassword  = EncryptionUtil.decryptString(initAuthorizationPassword);
            }
            catch (Exception ex) {
			    authorizationPassword = initAuthorizationPassword;
            }
		}
		String initWebFilesRoot = getServletConfig().getInitParameter("WebFilesRoot");//$NON-NLS-1$
		if (null != initWebFilesRoot) {
			webFilesRoot = initWebFilesRoot;
		}
		if (! webFilesRoot.startsWith("/")) {
			webFilesRoot = '/' + webFilesRoot;
		}
		if (! webFilesRoot.endsWith("/")) {
			webFilesRoot += '/';
		}
		String initServerInfosJspPath = getServletConfig().getInitParameter("ServerInfosJsp");//$NON-NLS-1$
		if (null != initServerInfosJspPath) {
			serverInfosJspPath = webFilesRoot + initServerInfosJspPath;
		}
		String initWebAppsListJspPath = getServletConfig().getInitParameter("WebAppsListJsp");//$NON-NLS-1$
		if (null != initWebAppsListJspPath) {
			webAppsListJspPath = webFilesRoot + initWebAppsListJspPath;
		}
		String initWebAppStatsJspPathJspPath = getServletConfig().getInitParameter("WebAppStatsJsp");//$NON-NLS-1$
		if (null != initWebAppStatsJspPathJspPath) {
			webAppStatsJspPath = webFilesRoot + initWebAppStatsJspPathJspPath;
		}
		String initSessionsListJspPath = getServletConfig().getInitParameter("SessionsListJsp");//$NON-NLS-1$
		if (null != initSessionsListJspPath) {
			sessionsListJspPath = webFilesRoot + initSessionsListJspPath;
		}
		String initSessionDetailJspPath = getServletConfig().getInitParameter("SessionDetailJsp");//$NON-NLS-1$
		if (null != initSessionDetailJspPath) {
			sessionDetailJspPath = webFilesRoot + initSessionDetailJspPath;
		}
	}
}