"""Allow2 API client for device pairing and quota checking."""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass
from typing import Any

import aiohttp
from aiohttp import ClientError, ClientResponseError, ClientTimeout

from .const import (
    API_BASE_URL,
    API_CHECK_ENDPOINT,
    API_PAIR_ENDPOINT,
    API_TIMEOUT,
    DEFAULT_DEVICE_NAME,
    DEFAULT_DEVICE_TOKEN,
)

_LOGGER = logging.getLogger(__name__)


@dataclass
class PairResult:
    """Result from device pairing."""

    user_id: int
    pair_id: int
    pair_token: str
    children: list[dict[str, Any]]

    @classmethod
    def from_response(cls, data: dict[str, Any]) -> PairResult:
        """Create PairResult from API response."""
        return cls(
            user_id=data["userId"],
            pair_id=data["pairId"],
            pair_token=data["token"],
            children=data.get("children", []),
        )


@dataclass
class CheckResult:
    """Result from quota check."""

    allowed: bool
    activities: dict[int, ActivityStatus]
    children: dict[int, ChildStatus]
    day_types: dict[str, Any]
    subscription: dict[str, Any]
    raw_response: dict[str, Any]


@dataclass
class ActivityStatus:
    """Status for a single activity."""

    activity_id: int
    name: str
    allowed: bool
    banned: bool
    remaining_seconds: int | None
    time_block_allowed: bool


@dataclass
class ChildStatus:
    """Status for a single child."""

    child_id: int
    name: str
    allowed: bool
    activities: dict[int, ActivityStatus]


class Allow2Error(Exception):
    """Base exception for Allow2 errors."""


class Allow2AuthError(Allow2Error):
    """Authentication error."""


class Allow2ConnectionError(Allow2Error):
    """Connection error."""


class Allow2ResponseError(Allow2Error):
    """Invalid response error."""


class Allow2API:
    """Allow2 API client.

    This client implements the device pairing mode for Allow2,
    which persists credentials on the device (Home Assistant) side.

    Usage:
        1. Call pair() with email/password to get credentials
        2. Store credentials (user_id, pair_id, pair_token)
        3. Call check() with stored credentials to check quotas
    """

    def __init__(
        self,
        session: aiohttp.ClientSession,
        device_token: str = DEFAULT_DEVICE_TOKEN,
        device_name: str = DEFAULT_DEVICE_NAME,
    ) -> None:
        """Initialize the Allow2 API client.

        Args:
            session: aiohttp client session for making requests
            device_token: Device token for Allow2 (default is Home Assistant token)
            device_name: Name to display in Allow2 dashboard
        """
        self._session = session
        self._device_token = device_token
        self._device_name = device_name
        self._timeout = ClientTimeout(total=API_TIMEOUT)

    @property
    def device_token(self) -> str:
        """Return the device token."""
        return self._device_token

    async def pair(self, email: str, password: str) -> PairResult:
        """Pair this device with an Allow2 account.

        This is the initial setup step. The returned credentials
        (user_id, pair_id, pair_token) should be stored and used
        for subsequent check() calls.

        Args:
            email: User's Allow2 account email
            password: User's Allow2 account password

        Returns:
            PairResult with user_id, pair_id, pair_token, and children

        Raises:
            Allow2AuthError: If authentication fails
            Allow2ConnectionError: If connection fails
            Allow2ResponseError: If response is invalid
        """
        url = f"{API_BASE_URL}{API_PAIR_ENDPOINT}"
        payload = {
            "user": email,
            "pass": password,
            "deviceToken": self._device_token,
            "name": self._device_name,
        }

        _LOGGER.debug("Pairing device with Allow2: %s", self._device_name)

        try:
            async with self._session.post(
                url,
                data=payload,
                timeout=self._timeout,
            ) as response:
                data = await response.json()

                _LOGGER.debug("Pair response status: %d", response.status)

                # Check for API-level errors in response
                if "error" in data:
                    error_msg = data.get("error", "Unknown error")
                    error_code = data.get("errorCode", 0)
                    _LOGGER.error(
                        "Allow2 pairing failed: %s (code: %d)",
                        error_msg,
                        error_code,
                    )
                    raise Allow2AuthError(error_msg)

                # Validate required fields
                required_fields = ["userId", "pairId", "token"]
                missing = [f for f in required_fields if f not in data]
                if missing:
                    _LOGGER.error("Missing fields in pair response: %s", missing)
                    raise Allow2ResponseError(
                        f"Missing required fields: {', '.join(missing)}"
                    )

                return PairResult.from_response(data)

        except aiohttp.ContentTypeError as err:
            _LOGGER.error("Invalid response content type: %s", err)
            raise Allow2ResponseError("Invalid response format") from err
        except ClientResponseError as err:
            _LOGGER.error("HTTP error during pairing: %s", err)
            if err.status in (401, 403):
                raise Allow2AuthError("Invalid credentials") from err
            raise Allow2ConnectionError(f"HTTP error: {err.status}") from err
        except ClientError as err:
            _LOGGER.error("Connection error during pairing: %s", err)
            raise Allow2ConnectionError(str(err)) from err
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout during pairing")
            raise Allow2ConnectionError("Request timed out") from err

    async def check(
        self,
        user_id: int,
        pair_id: int,
        pair_token: str,
        child_id: int,
        activities: list[int],
        timezone: str = "UTC",
        log: bool = True,
    ) -> CheckResult:
        """Check quota/allowance for a child and activities.

        This should be called with credentials obtained from pair().

        Args:
            user_id: User ID from pairing
            pair_id: Pair ID from pairing
            pair_token: Pair token from pairing
            child_id: ID of the child to check
            activities: List of activity IDs to check
            timezone: Timezone for the check (e.g., "America/New_York")
            log: Whether to log this check in Allow2 dashboard

        Returns:
            CheckResult with allowed status and activity details

        Raises:
            Allow2AuthError: If credentials are invalid
            Allow2ConnectionError: If connection fails
            Allow2ResponseError: If response is invalid
        """
        url = f"{API_BASE_URL}{API_CHECK_ENDPOINT}"
        payload = {
            "userId": user_id,
            "pairId": pair_id,
            "pairToken": pair_token,
            "deviceToken": self._device_token,
            "tz": timezone,
            "childId": child_id,
            "activities": ",".join(str(a) for a in activities),
            "log": "true" if log else "false",
        }

        _LOGGER.debug(
            "Checking quota for child %d, activities: %s",
            child_id,
            activities,
        )

        try:
            async with self._session.post(
                url,
                data=payload,
                timeout=self._timeout,
            ) as response:
                data = await response.json()

                _LOGGER.debug("Check response status: %d", response.status)

                # Check for API-level errors
                if "error" in data:
                    error_msg = data.get("error", "Unknown error")
                    _LOGGER.error("Allow2 check failed: %s", error_msg)
                    raise Allow2AuthError(error_msg)

                return self._parse_check_response(data)

        except aiohttp.ContentTypeError as err:
            _LOGGER.error("Invalid response content type: %s", err)
            raise Allow2ResponseError("Invalid response format") from err
        except ClientResponseError as err:
            _LOGGER.error("HTTP error during check: %s", err)
            if err.status in (401, 403):
                raise Allow2AuthError("Invalid credentials") from err
            raise Allow2ConnectionError(f"HTTP error: {err.status}") from err
        except ClientError as err:
            _LOGGER.error("Connection error during check: %s", err)
            raise Allow2ConnectionError(str(err)) from err
        except asyncio.TimeoutError as err:
            _LOGGER.error("Timeout during check")
            raise Allow2ConnectionError("Request timed out") from err

    def _parse_check_response(self, data: dict[str, Any]) -> CheckResult:
        """Parse the check API response into a CheckResult.

        Args:
            data: Raw API response dictionary

        Returns:
            Parsed CheckResult
        """
        # Parse overall allowed status
        allowed = data.get("allowed", False)

        # Parse activities
        activities_data = data.get("activities", {})
        activities = {}
        for activity_id_str, activity_info in activities_data.items():
            activity_id = int(activity_id_str)
            activities[activity_id] = ActivityStatus(
                activity_id=activity_id,
                name=activity_info.get("name", f"Activity {activity_id}"),
                allowed=activity_info.get("allowed", False),
                banned=activity_info.get("banned", False),
                remaining_seconds=activity_info.get("remaining"),
                time_block_allowed=activity_info.get("timeBlockAllowed", False),
            )

        # Parse children status
        children_data = data.get("children", {})
        children = {}
        for child_id_str, child_info in children_data.items():
            child_id = int(child_id_str)
            child_activities = {}
            for act_id_str, act_info in child_info.get("activities", {}).items():
                act_id = int(act_id_str)
                child_activities[act_id] = ActivityStatus(
                    activity_id=act_id,
                    name=act_info.get("name", f"Activity {act_id}"),
                    allowed=act_info.get("allowed", False),
                    banned=act_info.get("banned", False),
                    remaining_seconds=act_info.get("remaining"),
                    time_block_allowed=act_info.get("timeBlockAllowed", False),
                )
            children[child_id] = ChildStatus(
                child_id=child_id,
                name=child_info.get("name", f"Child {child_id}"),
                allowed=child_info.get("allowed", False),
                activities=child_activities,
            )

        return CheckResult(
            allowed=allowed,
            activities=activities,
            children=children,
            day_types=data.get("dayTypes", {}),
            subscription=data.get("subscription", {}),
            raw_response=data,
        )

    async def get_children(
        self,
        user_id: int,
        pair_id: int,
        pair_token: str,
    ) -> list[dict[str, Any]]:
        """Get list of children for the paired account.

        This performs a check with no specific child to get the
        full children list from the response.

        Args:
            user_id: User ID from pairing
            pair_id: Pair ID from pairing
            pair_token: Pair token from pairing

        Returns:
            List of children with their IDs and names
        """
        url = f"{API_BASE_URL}{API_CHECK_ENDPOINT}"
        payload = {
            "userId": user_id,
            "pairId": pair_id,
            "pairToken": pair_token,
            "deviceToken": self._device_token,
            "tz": "UTC",
            "log": "false",
        }

        try:
            async with self._session.post(
                url,
                data=payload,
                timeout=self._timeout,
            ) as response:
                data = await response.json()

                if "error" in data:
                    raise Allow2AuthError(data.get("error", "Unknown error"))

                children = []
                for child_id_str, child_info in data.get("children", {}).items():
                    children.append({
                        "id": int(child_id_str),
                        "name": child_info.get("name", f"Child {child_id_str}"),
                    })

                return children

        except (ClientError, asyncio.TimeoutError) as err:
            _LOGGER.error("Error getting children: %s", err)
            raise Allow2ConnectionError(str(err)) from err
